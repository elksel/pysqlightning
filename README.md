# Pysqlightning
## Make the SQlite3 library go FAST(er)

This pysqlite2 fork utilizes Howard Chu's [LMDB](https://github.com/LMDB/lmdb) to power Sqlite3, via his
[sqlightning](https://github.com/LMDB/sqlightning) port, adapted to work with Python by [Andrew Leech](https://github.com/andrewleech/pysqlightning).
My only current contribution is to fix an issue with the version of dbapi2 that made it not work with Python 2, and to update this doc to make
it more readily apparent how to build and install this library.

## Why use this library?

The backing store is *significantly* faster than the default sqlite3 B-tree implementation, and performs very well in comparison 
to both [other B-tree implementations and LSM databases](http://symas.com/mdb/ondisk/) for many diverse workloads. As well,
LMDB and Sqlightning are licensed via the OpenLDAP and public domain licenses, which are often easier to integrate in places
where BDB can no longer be used in (due to the usage of the AGPL license with BDB). This library should help you squeeze the
absolute maximum performance out of Sqlite.

## Future plans

* Better Docs
* Basic Tests
* Examine what it would take to move sqlightning to feature parity with sqlite 3.9.0.

## To Build/Install

#### Clone the repository

    $ git clone https://github.com/andrewleech/pysqlightning

#### Initialize and update the submodules

    $ git submodule init
    $ git submodule update

#### Run the static build

    pysqlightning$ python setup.py build_static

#### Build binary distribution OR install

    # Build binary distributions
    pysqlightning$ python setup.py bdist
    pysqlightning$ python setup.py bdist_egg

    # etc...

    # Install
    pysqlightning$ python setup.py install
    


# Original Docs

pysqlite
========

Python DB-API module for SQLite 3.

Online documentation can be found [here] (https://pysqlite.readthedocs.org/en/latest/sqlite3.html).
