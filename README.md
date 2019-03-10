Factorio Blueprints
===================

A command line tool to parse and manage blueprint strings from the game **[Factorio](https://www.factorio.com/)**.


## Database

The script will store blueprints as JSON files in a folder referred to as the database. By default the database is located in `./factorio-blueprints-db` relatively to this repository.

Blueprint books are stored as folders, containing one file per individual blueprint.

Single blueprints (not part of a blueprint book) are stored in a special folder named `Not a blueprint book`.

It is advised to manage the database folder as a separate git repository.


## Usage

Import a blueprint string:
* Raw in command line:

```
$ ./blueprints.py -s 0eNp9kDFrwzAQhf+KuVkqTk1I0ZitQ6eOJRhZPZLD1klIclIT/N8r2RRnaLsI7un0vfd0h24Y0Qfi1HbO9aDumxJBfTyM5Y6M41WOdGY9FC1NHkEBJbQggLUtkx6TszqRYxkNIRuUXpseZgHEn/gFajefBCAnSoQrchmmlkfbYcgLGyxGtN1AfJZWmwsxyuds5V2k4lBCZGAtYMpndghoyP+bIlsvedVDPQGD7jBXgvd196l6TdXNhT6K6kjJXHJOAVcMcTE9NPVuXzfNy/6wtap/Q8vlazf+21QdV0WbRFdsfx7/QZ+/AShRje0=
```

* From a file (one blueprint string per line):

`$ ./blueprints.py -f examples/test_blueprint_book.txt`

List blueprint database content:

```
$ ./blueprints.py -l
Blueprint Book: My Book/
 >> 000 - Science. It works, Bitches.json
```

Copy blueprint string to clipboard for import in Factorio:

`$ ./blueprints.py --raw -b "My Book" | clip`

More commands:

`$ ./blueprints.py --help`


## Requirements

* __Python 2.7.x__: http://www.python.org/download/


## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](./LICENSE)
