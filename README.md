# IRS_Migration

Repo for exploring state-to-state and county-to-county migration data, published by the Internal Revenue Service.

Setup
-----

First, you need to set up a local PostgreSQL database:

	$ psql
	# CREATE DATABASE [db_name];
	# \q

Now run the [load data script](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py):

	$ python load_data.py [db_name] [db_user] [db_password]

If you don't pass the database parameters when you initialize the script, you'll still be prompted to provide them.

A little more about how load_data.py works:

1.	[Request and parse](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L88-L90) the [page](http://www.irs.gov/uac/SOI-Tax-Stats-State-to-State-Migration-Database-Files) containing links to state-level migration files.

2.	[Iterate](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L92-L93) over links files found via the [get_files()](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L18-L46). This function [check](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L30-L32) to see if the given file is already in the data directory. If not, then it [download](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L34-L42) the file. 
	
	Note that we must the source files' [specify the original encoding](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L42) when writing their contents local copies. Ultimately, we want this data in UTF-8, so we also specify that encoding when [opening](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L40) the local file, [reading](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L127) from that local copy and [loading](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L58) into the database.

3. [Repeat these steps](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L96-L101) for the [county-level data](http://www.irs.gov/uac/SOI-Tax-Stats-County-to-County-Migration-Data-Files).

4.	Then for each file, [use csvkit](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L127) to figure out the layout of each file.

5.	Then create a [SQLAlchemy Table object](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L131) and call the create method to [create the database table](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L131).

6.	Finally, call [load_data()](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L49-L78), which determines the [dialect](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L52) of the .csv (e.g., the delimiter and quote character) and generates the [COPY FROM](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L54-L60) statement, [sets up a connection](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L68) and a [transaction](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L70), [executes](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L72-L76) the SQL, then [closes](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L78).
