import csvkit
import os
import requests
from bs4 import BeautifulSoup
import re
import psycopg2


def get_files(soup, url_pattern):

	for link in soup.findAll('a', href = url_pattern):

		path = link['href'].split('/',)

		file_name = path[len(path) - 1]

		print '   downloading ' + file_name

		response = requests.get('http://www.irs.gov/' + link['href']) # figure out how to do the url scheme better

		with open('downloads/' + file_name, 'w') as out_file:

			out_file.write(response.content)

# get state-level data
response = requests.get('http://www.irs.gov/uac/SOI-Tax-Stats-State-to-State-Migration-Database-Files')

soup = BeautifulSoup(response.content)

get_files(soup, re.compile(r'/file_source/pub/irs-soi/state.+\.+csv'))

# get county-level data
response = requests.get('http://www.irs.gov/uac/SOI-Tax-Stats-County-to-County-Migration-Data-Files')

soup = BeautifulSoup(response.content)

get_files(soup, re.compile(r'/file_source/pub/irs-soi/county.+\.+csv'))
