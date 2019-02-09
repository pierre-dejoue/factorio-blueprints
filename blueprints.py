#!/usr/bin/env python
"""
CLI to manage Factorio blueprints
"""

from __future__ import print_function

import argparse
import base64
import ConfigParser
import json
import os
import sys
import zlib



CONFIG_FILE = 'config.ini'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BLUEPRINT_SUPPORTED_VERSIONS = [0]


try:
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(SCRIPT_PATH, CONFIG_FILE))

    BLUEPRINT_VERSION = config.getint('blueprints', 'version')
    DB_PATH = config.get('blueprints-db', 'location')
    NO_BOOK_NAME = config.get('blueprints-db', 'not_a_book_special_folder')
except Exception as err:
    print('Error parsing ' + CONFIG_FILE + ': ' + str(err))
    sys.exit(-1)




def full_db_path(db_path = DB_PATH):
    return os.path.join(SCRIPT_PATH, db_path)


def create_db_directories(db_path = DB_PATH, not_a_book = NO_BOOK_NAME):
    """create DB if not existing"""
    db_directory = full_db_path(db_path)
    if not os.path.exists(db_directory):
        print('Make directory: ' + db_directory)
        os.makedirs(db_directory)
    db_not_a_book_directory = os.path.join(db_directory, not_a_book)
    if not os.path.exists(db_not_a_book_directory):
        print('Make directory: ' + db_not_a_book_directory)
        os.makedirs(db_not_a_book_directory)


def parse_blueprint_string(blueprint_str):
    assert int(blueprint_str[0]) in BLUEPRINT_SUPPORTED_VERSIONS, 'Blueprint version number ' + blueprint_str[0] + ' is not among the supported versions: ' + str(BLUEPRINT_SUPPORTED_VERSIONS)
    return zlib.decompress(base64.b64decode(blueprint_str[1:]))


def generate_blueprint_string(blueprint_json):
    return str(BLUEPRINT_VERSION) +  base64.b64encode(zlib.compress(blueprint_json))


def delete_book_content(book_directory):
    for file in os.listdir(book_directory):
        file_path = os.path.join(book_directory, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as err:
            print('Error deleting blueprint file [' + file_path + ']: ' + str(err))


def store_blueprint_book(book_obj, db_path = DB_PATH):
    book_name = book_obj['blueprint_book']['label'] if 'label' in book_obj['blueprint_book'].keys() else 'no-name'

    # Create blueprint book folder, or erase its content if existing
    db_book_directory = os.path.join(full_db_path(db_path), book_name)
    if not os.path.exists(db_book_directory):
        print('Book Created: ' + db_book_directory)
        os.makedirs(db_book_directory)
    else:
        print('Book Updated: ' + db_book_directory)
        delete_book_content(db_book_directory)

    # Create or update individual blueprints
    for blueprint_elt in book_obj['blueprint_book']['blueprints']:
        prefix_index = '{0:03d} - '.format(blueprint_elt['index'])
        blueprint_obj = { 'blueprint' : blueprint_elt['blueprint'] }
        try:
            store_single_blueprint(blueprint_obj, prefix_index, book_name, db_path)
        except Exception as err:
            print('Error writing blueprint file: ' + str(err))


def store_single_blueprint(blueprint_obj, prefix_name, book_name = NO_BOOK_NAME, db_path = DB_PATH):
    blueprint_name = blueprint_obj['blueprint']['label'] if 'label' in blueprint_obj['blueprint'].keys() else 'no-name'
    rel_db_path = os.path.join(book_name, prefix_name + blueprint_name + '.json')
    full_path = os.path.join(full_db_path(db_path), rel_db_path)
    if os.path.exists(full_path):
        print('Blueprint Updated: ' + rel_db_path)
    else:
        print('Blueprint Created: ' + rel_db_path)
    fp = open(full_path, 'w')
    json.dump(blueprint_obj, fp, indent=2, separators=(',', ': '))


def store_db_from_string(blueprint_raw_string, book_name = NO_BOOK_NAME, db_path = DB_PATH):
    result = 0
    try:
        blueprint_json = parse_blueprint_string(blueprint_raw_string)
        blueprint_obj = json.loads(blueprint_json)
        if 'blueprint_book' in blueprint_obj.keys():
            store_blueprint_book(blueprint_obj, db_path)
        elif 'blueprint' in blueprint_obj.keys():
            store_single_blueprint(blueprint_obj, '', book_name, db_path)
        else:
            print('ParsingError: Could not identify the type of blueprint ' + blueprint_obj.keys())
            result = -1
    except AssertionError as err:
        print('AssertionError: ' + str(err))
        return -1
    except IOError as err:
        print('IOError: ' + str(err))
        return -1
    except Exception as err:
        print('Exception: ' + str(err))
        return -1

    return result


def list_book_contents(book_name, db_path = DB_PATH):
    content = []
    book_path = os.path.join(full_db_path(db_path), book_name)
    for file in os.listdir(book_path):
        file_path = os.path.join(book_path, file)
        if os.path.isfile(file_path) and file[-5:] == ".json":
            content.append(file)
    return content


def list_db(db_path = DB_PATH):
    content_singles = []
    for file in os.listdir(full_db_path(db_path)):
        content = []
        if file == NO_BOOK_NAME:
            # Print that one last
            content_single = list_book_contents(NO_BOOK_NAME, db_path)
        elif file[0] != '.' and os.path.isdir(os.path.join(full_db_path(db_path), file)):
            content = list_book_contents(file, db_path)
        if content:
            print('Blueprint Book: ' + file + '/')
            for bp_file in content:
                print(' >> ' + bp_file)

    if content_singles:
        print('Individual Blueprints:')
        for bp_file in content_singles:
            print(' >> ' + bp_file)


def main():
    result = 0
    parser = argparse.ArgumentParser(description='Manage Factorio blueprints')
    parser.add_argument('-s', '--store-db-from-strings', metavar='raw_string', dest='blueprint_strings', nargs='+', help='Store blueprints from raw strings')
    parser.add_argument('-f', '--store-db-from-files', metavar='file', dest='blueprint_files', nargs='+', help='Store blueprints from files, one raw blueprint string per line')
    parser.add_argument('-l', '--list', dest='list_db', action='store_true', help='List database content')
    args = parser.parse_args()

    create_db_directories()

    if args.blueprint_strings:
        for blueprint_string in args.blueprint_strings:
            store_db_from_string(blueprint_string)
    elif args.blueprint_files:
        for blueprint_file in args.blueprint_files:
            print('Opening file: ' + blueprint_file)
            fp = open(blueprint_file, 'r')
            for blueprint_string in fp:
                store_db_from_string(blueprint_string.strip())
    elif args.list_db:
        list_db()
    else:
        print("Error: no argument")
        parser.print_help()
        result = -1

    return result


if __name__ == "__main__":
    main()
