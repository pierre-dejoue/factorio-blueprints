#!/usr/bin/env python
"""
Command line tool to manage blueprint strings from the game Factorio (https://www.factorio.com/)
"""


import argparse
import base64
import configparser
import json
import re
import os
import sys
import zlib
from collections.abc import Callable


CONFIG_FILE = 'config.ini'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
EXCHANGE_STRINGS_SUPPORTED_VERSIONS = [0]


try:
    config = configparser.ConfigParser()
    config.read(os.path.join(SCRIPT_PATH, CONFIG_FILE))

    EXCHANGE_STRINGS_DEFAULT_VERSION = config.getint('blueprints', 'version')
    DB_PATH = config.get('blueprints-db', 'location')
except Exception as err:
    print('Error parsing ' + CONFIG_FILE + ': ' + str(err))
    sys.exit(-1)


assert EXCHANGE_STRINGS_DEFAULT_VERSION in EXCHANGE_STRINGS_SUPPORTED_VERSIONS, 'Blueprint version number in config.ini ' + str(EXCHANGE_STRINGS_DEFAULT_VERSION) + ' is not among the supported versions: ' + str(EXCHANGE_STRINGS_SUPPORTED_VERSIONS)


ENTITY_RENAMING_0_16_TO_0_17 = {
    'science-pack-1': 'automation-science-pack',
    'science-pack-2': 'logistic-science-pack',
    'science-pack-3': 'chemical-science-pack',
    'high-tech-science-pack': 'utility-science-pack',
    'raw-wood': 'wood',
}


def full_db_path(db_path: str = DB_PATH) -> str:
    return os.path.join(SCRIPT_PATH, db_path)


def create_db_directories(db_path: str = DB_PATH) -> None:
    """create DB if not existing"""
    db_directory = full_db_path(db_path)
    if not os.path.exists(db_directory):
        print('Make directory: ' + db_directory)
        os.makedirs(db_directory)


def parse_bp_exchange_string(blueprint_base64: str) -> str:
    version = int(blueprint_base64[0])
    assert version in EXCHANGE_STRINGS_SUPPORTED_VERSIONS, 'Blueprint version number ' + str(version) + ' is not among the supported versions: ' + str(EXCHANGE_STRINGS_SUPPORTED_VERSIONS)
    return zlib.decompress(base64.b64decode(blueprint_base64[1:])).decode()


def generate_bp_exchange_string(blueprint_json: str) -> str:
    return str(EXCHANGE_STRINGS_DEFAULT_VERSION) + base64.b64encode(zlib.compress(blueprint_json.encode())).decode()


def parse_bp_exchange_string_as_json_object(blueprint_base64: str) -> dict:
    blueprint_json_str = parse_bp_exchange_string(blueprint_base64)
    return json.loads(blueprint_json_str)


def generate_bp_exchange_string_from_json_object(blueprint_obj: dict) -> str:
    # Ensure the most compact JSON format
    json_str = json.dumps(blueprint_obj, sort_keys=True, separators=(',', ':'))
    return generate_bp_exchange_string(json_str)


def decode_game_version(version: int):
    version_major = (version & 0x0FFFF000000000000) >> 48
    version_minor = (version & 0x00000FFFF00000000) >> 32
    version_patch = (version & 0x000000000FFFF0000) >> 16
    version_dev   = (version & 0x0000000000000FFFF)
    version_str = '{}.{}.{}'.format(version_major, version_minor, version_patch)
    if version_dev != 0:
        version_str = '{}.{}'.format(version_str, version_dev)
    return version_str


def parse_game_version(blueprint_obj: dict) -> str:
    blueprint_subobj = {}
    for key in ['blueprint', 'blueprint_book']:
        if key in blueprint_obj:
            blueprint_subobj = blueprint_obj[key]
    return decode_game_version(blueprint_subobj['version']) if 'version' in blueprint_subobj else 'unknonwn'


def parse_blueprint_name(blueprint_obj: dict) -> str:
    blueprint_subobj = {}
    for key in ['blueprint', 'blueprint_book']:
        if key in blueprint_obj:
            blueprint_subobj = blueprint_obj[key]
    return blueprint_subobj['label'] if 'label' in blueprint_subobj else 'no-name'


def pretty_print_json(blueprint_obj: dict, fp = sys.stdout) -> None:
    json.dump(blueprint_obj, fp, sort_keys=True, indent=2, separators=(',', ': '))


def print_blueprint_book_contents(book_obj: dict, max_recursion_level: int = 0, recursion_level: int = 0) -> None:
    assert 'blueprint_book' in book_obj, 'Only accept blueprint book as input'
    INDENTATION_PER_LEVEL = 2
    book_contents = book_obj['blueprint_book']['blueprints']
    for blueprint_elt in book_contents:
        blueprint_elt_index = blueprint_elt['index'] if 'index' in blueprint_elt else -1
        blueprint_elt_index_str = '#{0:03d}'.format(blueprint_elt_index) if blueprint_elt_index >= 0 else '#'
        blueprint_elt_type = 'Unknown'
        blueprint_elt_descr = parse_blueprint_name(blueprint_elt)
        if 'blueprint_book' in blueprint_elt:
            blueprint_elt_type = 'Blueprint Book'
        elif 'blueprint' in blueprint_elt:
            blueprint_elt_type = 'Blueprint'
        else:
            blueprint_elt_descr = str(blueprint_elt.keys())
        print('{0}{1} {2}: {3}'.format((INDENTATION_PER_LEVEL * (recursion_level + 1) * ' '), blueprint_elt_index_str, blueprint_elt_type, blueprint_elt_descr))
        # Recursive call on blueprint books
        if 'blueprint_book' in blueprint_elt and recursion_level < max_recursion_level:
            print_blueprint_book_contents(blueprint_elt, max_recursion_level, recursion_level + 1)


def info_from_blueprint_book(book_obj: dict, max_recursion_level: int = 0) -> None:
    assert 'blueprint_book' in book_obj, 'Not a blueprint book'
    book_name = parse_blueprint_name(book_obj)
    book_version = parse_game_version(book_obj)
    print('Book: ' + book_name)
    print('Version: ' + book_version)
    print('Contents:')
    print_blueprint_book_contents(book_obj, max_recursion_level)


def info_from_single_blueprint(blueprint_obj: dict, blueprint_index: int = -1) -> None:
    assert 'blueprint' in blueprint_obj, 'Not a blueprint'
    blueprint_name = parse_blueprint_name(blueprint_obj)
    blueprint_version = parse_game_version(blueprint_obj)
    print('Blueprint: ' + blueprint_name)
    print('Version: ' + blueprint_version)


def info_from_blueprint_object(blueprint_obj: dict, max_recursion_level: int = 0) -> int:
    result = 0
    if 'blueprint_book' in blueprint_obj:
        info_from_blueprint_book(blueprint_obj, max_recursion_level)
    elif 'blueprint' in blueprint_obj:
        info_from_single_blueprint(blueprint_obj)
    else:
        print('ParsingError: Could not identify the type of blueprint ' + str(blueprint_obj.keys()))
        result = -1
    return result


def find_index_in_blueprint_book(blueprint_obj: dict, index: int) -> dict:
    if 'blueprint_book' not in blueprint_obj:
        return None
    book_contents = blueprint_obj['blueprint_book']['blueprints']
    for blueprint_elt in book_contents:
        blueprint_elt_index = blueprint_elt['index'] if 'index' in blueprint_elt else -1
        if blueprint_elt_index == index:
            return blueprint_elt
    return None


def get_book_in_json(book_name: str, contents: str, version: int, active_index: int = 0) -> str:
    assert contents, 'Empty book [' + book_name + ']'
    blueprints = [{'blueprint': bp_parsed_file['blueprint'], 'index': bp_parsed_file['index']} for bp_parsed_file in contents]
    blueprint_book = {
        'blueprint_book': {
          'active_index': active_index,
          'blueprints': blueprints,
          'item': 'blueprint-book',
          'label': book_name,
          'version': version
        }
    }
    return generate_bp_exchange_string_from_json_object(blueprint_book)


def update_entity_names(blueprint_obj: dict, entity_mapping: dict) -> bool:
    assert blueprint_obj

    def func_str(entity: dict, k: str):
        assert k in entity
        assert isinstance(entity[k], str)
        if entity[k] in entity_mapping:
            entity[k] = entity_mapping[entity[k]]
            return True
        return False

    def do_nothing(_entity: dict, _k: str): return False

    return walk_json_obj_and_map(blueprint_obj, func_str, do_nothing, do_nothing)


ProcessBlueprint = Callable[[dict, dict], bool]


def walk_json_obj_and_map(json_obj, process_str: ProcessBlueprint, process_int: ProcessBlueprint, process_float: ProcessBlueprint) -> bool:
    modified = False
    if isinstance(json_obj, dict):
        for (key, value) in json_obj.items():
            if isinstance(value, str):
                modified = modified | process_str(json_obj, key)
            elif isinstance(value, int):
                modified = modified | process_int(json_obj, key)
            elif isinstance(value, float):
                modified = modified | process_float(json_obj, key)
            else:
                modified = modified | walk_json_obj_and_map(value, process_str, process_int, process_float)
    elif isinstance(json_obj, list):
        for elt in json_obj:
            modified = modified | walk_json_obj_and_map(elt, process_str, process_int, process_float)
    else:
        pass
    return modified


def map_blueprint_object(blueprint_obj: dict, process: ProcessBlueprint, json_pretty_print: bool) -> None:
    if process(blueprint_obj):
        print('Updated Blueprint:')
        if json_pretty_print:
            json.dump(blueprint_obj, sys.stdout, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            print(generate_bp_exchange_string_from_json_object(blueprint_obj))
    else:
        print('Not modified')


def process_blueprint_json_string(blueprint_json_str: str, args: argparse.Namespace) -> None:
    if args.raw:
        assert not args.json,           'Incompatible options --raw and --json'
        assert not args.update_to_0_17, 'Incompatible options --raw and --update-to-0.17'
        assert not args.index,          'Incompatible options --raw and --index'
        print(blueprint_json_str)
    else:
        blueprint_obj = json.loads(blueprint_json_str)
        # --name
        if args.bp_name:
            print(parse_blueprint_name(blueprint_obj))
            return
        # --version
        if args.bp_version:
            print(parse_game_version(blueprint_obj))
            return
        # --index
        if args.index is not None:
            blueprint_obj = find_index_in_blueprint_book(blueprint_obj, args.index)
        if not blueprint_obj:
            print('Not found')
            return
        # Remaining options: --update-to-0.17, --json, --raw, --exchange and no option (= print info)
        if args.update_to_0_17:
            def func_update_to_0_17(obj: dict) -> bool:
                return update_entity_names(obj, ENTITY_RENAMING_0_16_TO_0_17)
            map_blueprint_object(blueprint_obj, func_update_to_0_17, args.json)
        elif args.json:
            pretty_print_json(blueprint_obj)
        elif args.exchange:
            print(generate_bp_exchange_string_from_json_object(blueprint_obj))
        else:
            # By default, print information about the blueprint
            info_from_blueprint_object(blueprint_obj, args.max_recursion_level)


def main():
    result = 0
    parser = argparse.ArgumentParser(description='Manage blueprint exchange strings from the game Factorio (https://www.factorio.com/)')
    parser.add_argument('-s', '--from-string', metavar='EXCHANGE_STRING', dest='bp_exchange_string', nargs=1, help='From a blueprint exchange string')
    parser.add_argument('-f', '--from-file', metavar='FILE', dest='blueprint_file', nargs=1, help='From a file with one blueprint exchange string per line')
    parser.add_argument('--index', metavar='INDEX_IN_BOOK', type=int, dest='index', help='Index of an element in a blueprint book')
    parser.add_argument('--json', dest='json', action='store_true', help='Print out the blueprint as pretty-printed JSON')
    parser.add_argument('--raw', dest='raw', action='store_true', help='Print out the decoded exchange string')
    parser.add_argument('--exchange', dest='exchange', action='store_true', help='Print out the exchange string')
    parser.add_argument('--name', dest='bp_name', action='store_true', help='Print out the name of the blueprint')
    parser.add_argument('--version', dest='bp_version', action='store_true', help='Print out the version of the game that generated the blueprint')
    parser.add_argument('-l', '--max-recursion-level', metavar='LEVEL', type=int, dest='max_recursion_level', default=0, help='Max recursion level while traversing blueprint books. Default: 0 (only the first level)')
    parser.add_argument('--update-to-0.17', dest='update_to_0_17', action='store_true', help='Update some entity names for 0.17')
    args = parser.parse_args()

    # Parse blueprints and blueprint books
    if args.bp_exchange_string:
        assert not args.blueprint_file, 'Incompatible options -s and -f'
        blueprint_json_str = parse_bp_exchange_string(args.bp_exchange_string[0])
        process_blueprint_json_string(blueprint_json_str, args)
    elif args.blueprint_file:
        assert not args.bp_exchange_string, 'Incompatible options -f and -s'
        blueprint_file = args.blueprint_file[0]
        #print('Opening file: ' + blueprint_file)
        with open(blueprint_file, 'rt') as f:
            for bp_exchange_string in f:
                blueprint_json_str = parse_bp_exchange_string(bp_exchange_string.strip())
                process_blueprint_json_string(blueprint_json_str, args)

    return result


if __name__ == "__main__":
    main()
