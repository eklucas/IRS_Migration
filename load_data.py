# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import os
import requests
from bs4 import BeautifulSoup
import re
from sys import argv
from getpass import getpass
from csvkit import table, sql, sniffer
from csvkit.table import Table
import codecs

start_time = datetime.now()
print 'Started at ' + str(start_time)


def get_files(soup, url_scheme, url_pattern):
	# Pass soup object containing links, plus url scheme of site and regex pattern for url links
	# Searches for file links, downloads files and returns a list of file names

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


def load_file(csv_file, db_engine):
	# Pass file object and SQLAlchemy db engine, builds and runs a COPY FROM statement

	dialect = sniffer.sniff_dialect(csv_file.read())

	copy_from_sql = '''COPY {table_name} 
						FROM '{file_w_path}'
						DELIMITER '{delimiter}'
						QUOTE '{quote_character}'
						ENCODING 'UTF8'
						CSV
						HEADER;'''.format(
								  table_name = csv_file.name.lstrip('data/').rstrip('.csv')
								, file_w_path = os.getcwd() + '/' + csv_file.name
								, delimiter = dialect.delimiter
								, quote_character = dialect.quotechar
								# , escape_character = '' if dialect.escapechar is None else dialect.escapechar 
							)

	conn = db_engine.connect() 

	t = conn.begin()

	try:
		conn.execute(copy_from_sql)
		t.commit()
	except:
		t.rollback()

	conn.close()



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

	print '   Opening {} ({})...'.format(f, datetime.now() - start_time)

	from_file = Table.from_csv(codecs.open('data/{}'.format(f), 'rU'), name = f.rstrip('.csv'), encoding = 'utf-8') # Here be some overhead

	print '   Making table object ({})...'.format(datetime.now() - start_time)

	sql_table = sql.make_table(from_file)

	print '   Creating SQL table ({})...'.format(datetime.now() - start_time)

	sql_table.create(engine, checkfirst=True)

	print '   Loading {} ({})...'.format(f, datetime.now() - start_time)

	load_file(codecs.open('data/{}'.format(f), 'rU'), engine)

	print '-----------------'

print 'fin.'
