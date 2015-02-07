# IRS_Migration

Repo for exploring state-to-state and county-to-county migration data, published by the Internal Revenue Service.

Setup
-----

First, you need to set up a local PostgreSQL database:

	$ psql
	# CREATE DATABASE [db_name];
	# \q

Now run the [load data script](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py):

	$ python load_data.py

