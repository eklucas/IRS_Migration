# IRS_Migration

Repo for exploring state-to-state and county-to-county migration data, published by the Internal Revenue Service.

Setup
-----

First, you need to set up a local PostgreSQL database:

	$ psql
	# CREATE DATABASE [db_name];
	# \q

Now run the [load data](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py) script:

	$ python load_data.py [db_name] [db_user] [db_password]

If you forget to pass the database parameters when you initialize the script, you'll still be prompted to provide them. Also note that the database user you specify will also need read permissions on the data downloaded by the script. So if you are logging into the database with the "postgres" role, this might be a problem. You could either manual set the permissions on the file to allow "Everyone" to read them or, better yet, create a new database role for your user account (Note that this might require you to run 'createdb' from the terminal if your PostgreSQL installation process did not set up a default database for the user OS user account).

A little more about how load_data.py works:

1.	[Request and parse](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L117-L119) the page with links to [state-level migration](http://www.irs.gov/uac/SOI-Tax-Stats-State-to-State-Migration-Database-Files) files.

2. [Iterate](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L121-L122) over links to files found via [get_files()](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L18-L46). This function [checks](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L31-L33) to see if the given file is already in the data directory. If not, then it [downloads](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L35-L43) the file. 
	
	Note that we [specify the original encoding](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L42) for the source files when writing their contents to local copies. Ultimately, we want this data in UTF-8, so we also specify that encoding when [opening](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L40) the local file, [reading](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L127) from that local copy and [loading](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L58) into the database.

3. [Repeat these steps](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L124-L130) for the [county-level files](http://www.irs.gov/uac/SOI-Tax-Stats-County-to-County-Migration-Data-Files).

4.	Set up a [database connection](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L134-L147) and a SQLAlchemy [engine](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L149).

5.	Then [for each file](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L151-L153), call [load_data()](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L49-L107), which has several actions:

	*	[Open](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L58) the .csv file.
	*	Determine the file's [dialect](https://github.com/onyxfish/csvkit/blob/master/csvkit/sniffer.py).
	*	Call the [from_csv() method](https://github.com/onyxfish/csvkit/blob/master/csvkit/table.py#L189-L257) of csvkit's Table class. This method infers the data types of each column (hence the overhead).
	*	Call [csvkit's make_table() method](https://github.com/onyxfish/csvkit/blob/master/csvkit/sql.py#L77-L89) to create a SQLAlchemy Table object.
	*	Call the SQLAlchemy Table object's [create() method](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L131) which generates and runs the CREATE TABLE... statement and runs it in the database.
	*	Generate the [COPY FROM](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L81-L93) statement, [set up a connection](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L95) and a [transaction](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L97), [execute](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L99-L101) the SQL ([or print](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L102-L105) the failed statement), then [close](https://github.com/gordonje/IRS_Migration/blob/master/load_data.py#L107) the connection.

