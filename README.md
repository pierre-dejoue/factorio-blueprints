Factorio Blueprints
===================

A command line tool to parse and manage blueprint exchange strings from the game **[Factorio](https://www.factorio.com/)**.

![Python3](http://img.shields.io/badge/python-3-blue.svg?v=1)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](./LICENSE)

## Usage

Read a blueprint exchange string:

* Raw string directly in the command line:

```
./blueprints.py -s 0eNp9kDFrwzAQhf+KuVkqTk1I0ZitQ6eOJRhZPZLD1klIclIT/N8r2RRnaLsI7un0vfd0h24Y0Qfi1HbO9aDumxJBfTyM5Y6M41WOdGY9FC1NHkEBJbQggLUtkx6TszqRYxkNIRuUXpseZgHEn/gFajefBCAnSoQrchmmlkfbYcgLGyxGtN1AfJZWmwsxyuds5V2k4lBCZGAtYMpndghoyP+bIlsvedVDPQGD7jBXgvd196l6TdXNhT6K6kjJXHJOAVcMcTE9NPVuXzfNy/6wtap/Q8vlazf+21QdV0WbRFdsfx7/QZ+/AShRje0=
```

* From a file (one exchange string per line):

`./blueprints.py -f tests/examples/blueprint_book.txt`

By default the script will parse the blueprint exchange string and display a summary of its contents:

```
$ python ./blueprints.py -f ./factorio-blueprints-db/blueprints/base_game/railway.txt
Opening file: ./factorio-blueprints-db/blueprints/base_game/railway.txt
Book: Railway
Version: 1.1.110
Contents:
  Blueprint: Ore Station - In 1-2 train
  Blueprint: Ore Station - Out 1-2 train
  Blueprint: Straight 2-way block
  Blueprint: T for  two-way rails
  Blueprint: Waiting Area for 1-2 trains
```

More commands:

`./blueprints.py --help`

## Requirements

* __Python 3.x__: http://www.python.org/download/

Currently there are no packages required. Should the need arise:

`pip install -r requirements.txt`

## Unit Tests

`python -m unittest -v`
