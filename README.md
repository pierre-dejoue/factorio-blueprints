Factorio Blueprints
===================

Command line tool to parse and manage Factorio blueprint strings.


## Database

The script will store blueprints as JSON files in a folder referred to as the database. The default location of the database is folder `factorio-blueprints-db` located in the same direcotry as the Pyhon script.

Blueprint books are stored as folders, containing one file per individual blueprint.

Single blueprints (not part of a blueprint book) are stored in a special folder named `not-a-blueprint-book`.

It is advised to manage the database folder as a separate git repository.


## Requirements

* __Python 2.7.x__
  * http://www.python.org/download/


## Usage Notes

`python -u blueprints.py --help`

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](./LICENSE)
