# -*- coding: utf-8 -*-

import os
import requests
from bs4 import BeautifulSoup
import re

from sys import argv
from getpass import getpass
import psycopg2

from csvkit import table, sql
from table import Table

import codecs


def get_files(soup, url_scheme, url_pattern):

	files = []

	for link in soup.findAll('a', href = url_pattern):

		path = link['href'].split('/',)

		file_name = path[len(path) - 1]

		if os.path.isfile('data/' + file_name):

			print '   found file: {}...'.format(file_name)

		else:

			print '   downloading: {}...'.format(file_name)

			response = requests.get(url_scheme + link['href'])

			with codecs.open('data/' + file_name, 'w', 'utf-8') as out_file:

				out_file.write(response.content.decode('latin-1'))

		files.append(file_name)

	return files


url_scheme = 'http://www.irs.gov/'

in_files = []


# get state-level data
response = requests.get(url_scheme + 'uac/SOI-Tax-Stats-State-to-State-Migration-Database-Files')

soup = BeautifulSoup(response.content)

for i in get_files(soup, url_scheme, re.compile(r'/file_source/pub/irs-soi/state.+\.+csv')):
	in_files.append(i)

# get county-level data
response = requests.get(url_scheme + 'uac/SOI-Tax-Stats-County-to-County-Migration-Data-Files')

soup = BeautifulSoup(response.content)

for i in get_files(soup, url_scheme, re.compile(r'/file_source/pub/irs-soi/county.+\.+csv')):
	in_files.append(i)


# Set up database connection
try:
	db = argv[1]
except IndexError:
	db = raw_input("Enter db name:")

try:
	user = argv[2]
except IndexError:
	user = raw_input("Enter db user:")

try:
	password = argv[3]
except IndexError:
	password = getpass("Enter db password:")

engine = sql.create_engine('postgresql+psycopg2://{0}:{1}@localhost/{2}'.format(user, password, db))


for f in in_files:

	print '   Making {}...'.format(f)

	the_file = codecs.open('data/{}'.format(f), 'rU')

	from_file = Table.from_csv(the_file, name = f, encoding = 'utf-8')

	sql_table = sql.make_table(from_file)

	sql_table.create(engine, checkfirst=True)

