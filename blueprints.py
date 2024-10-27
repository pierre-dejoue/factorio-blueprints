#!/usr/bin/env python
"""
Command line tool to manage blueprint exchange strings from the game Factorio (https://www.factorio.com/)
"""
__author__ = "Pierre DEJOUE"
__copyright__ = "Copyright (c) 2019 Pierre DEJOUE"
__license__ = "MIT License"
__version__ = "0.1"


import argparse
import configparser
import json
import os
import sys
from collections.abc import Callable
from factorio_game.exchange_string import blueprints


CONFIG_FILE = 'config.ini'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


try:
    config = configparser.ConfigParser()
    config.read(os.path.join(SCRIPT_PATH, CONFIG_FILE))

    EXCHANGE_STRINGS_VERSION = config.getint('blueprints', 'version', fallback = blueprints.DEFAULT_EXCHANGE_STRINGS_VERSION)
    DB_PATH = config.get('blueprints-db', 'location')
except Exception as err:
    print('Error parsing ' + CONFIG_FILE + ': ' + str(err))
    sys.exit(-1)


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


def pretty_print_json(blueprint_obj: dict, fp = sys.stdout) -> None:
    json.dump(blueprint_obj, fp, sort_keys=True, indent=2, separators=(',', ': '))


def pretty_print_bp_type(bp_type: blueprints.Type, blueprint_obj: dict) -> str:
    if bp_type:
        return ' '.join([ substr.capitalize() for substr in bp_type.value.replace('_', ' ').split()])
    return str(blueprint_obj.keys())


def print_blueprint_book_contents(book_obj: dict, max_recursion_level: int = 0, recursion_level: int = 0) -> None:
    assert 'blueprint_book' in book_obj, 'Only accept blueprint book as input'
    book_contents = book_obj['blueprint_book']['blueprints']
    for blueprint_elt in book_contents:
        blueprint_elt_index = blueprint_elt['index'] if 'index' in blueprint_elt else -1
        blueprint_elt_index_str = f'#{blueprint_elt_index:03d}' if blueprint_elt_index >= 0 else '#'
        blueprint_elt_type = blueprints.read_blueprint_type(blueprint_elt)
        blueprint_elt_type_str = pretty_print_bp_type(blueprint_elt_type, blueprint_elt)
        blueprint_elt_descr = blueprints.read_blueprint_name(blueprint_elt)
        indentation = str(2 * (recursion_level + 1) * ' ')
        print(f'{indentation}{blueprint_elt_index_str} {blueprint_elt_type_str}: {blueprint_elt_descr}')
        # Recursive call on blueprint books
        if 'blueprint_book' in blueprint_elt and recursion_level < max_recursion_level:
            print_blueprint_book_contents(blueprint_elt, max_recursion_level, recursion_level + 1)


def info_from_blueprint_book(book_obj: dict, max_recursion_level: int = 0) -> None:
    assert 'blueprint_book' in book_obj, 'Not a blueprint book'
    book_name = blueprints.read_blueprint_name(book_obj)
    book_version = blueprints.parse_game_version(book_obj)
    print('Blueprint Book: ' + book_name)
    print('Version: ' + book_version)
    print('Contents:')
    print_blueprint_book_contents(book_obj, max_recursion_level)


def info_from_single_blueprint(blueprint_obj: dict) -> None:
    blueprint_name = blueprints.read_blueprint_name(blueprint_obj)
    blueprint_type = blueprints.read_blueprint_type(blueprint_obj)
    blueprint_type_str = pretty_print_bp_type(blueprint_type, blueprint_obj)
    blueprint_version = blueprints.parse_game_version(blueprint_obj)
    print('Blueprint: ' + blueprint_name)
    if blueprint_type != blueprints.Type.BP:
        print('Type: ' + blueprint_type_str)
    print('Version: ' + blueprint_version)


def info_from_blueprint_object(blueprint_obj: dict, max_recursion_level: int = 0) -> None:
    bp_type = blueprints.read_blueprint_type(blueprint_obj)
    if bp_type == blueprints.Type.BOOK:
        info_from_blueprint_book(blueprint_obj, max_recursion_level)
    else:
        # All the other types, or an unknown type (bp_type is None)
        info_from_single_blueprint(blueprint_obj)


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
    blueprint_list = [{'blueprint': bp_parsed_file['blueprint'], 'index': bp_parsed_file['index']} for bp_parsed_file in contents]
    blueprint_book = {
        'blueprint_book': {
          'active_index': active_index,
          'blueprints': blueprint_list,
          'item': 'blueprint-book',
          'label': book_name,
          'version': version
        }
    }
    return blueprints.generate_exchange_string_from_json_object(blueprint_book, EXCHANGE_STRINGS_VERSION)


def update_entity_names(blueprint_obj: dict, entity_mapping: dict) -> bool:
    assert blueprint_obj

    def func_str(entity: dict, k: str):
        assert k in entity
        assert isinstance(entity[k], str)
        if entity[k] in entity_mapping:
            entity[k] = entity_mapping[entity[k]]
            return True
        return False

    def do_nothing(_entity: dict, _k: str):
        return False

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
            print(blueprints.generate_exchange_string_from_json_object(blueprint_obj, EXCHANGE_STRINGS_VERSION))
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
            print(blueprints.read_blueprint_name(blueprint_obj))
            return
        # --version
        if args.bp_version:
            print(blueprints.parse_game_version(blueprint_obj))
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
            print(blueprints.generate_exchange_string_from_json_object(blueprint_obj, EXCHANGE_STRINGS_VERSION))
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
        blueprint_json_str = blueprints.parse_exchange_string(args.bp_exchange_string[0])
        process_blueprint_json_string(blueprint_json_str, args)
    elif args.blueprint_file:
        assert not args.bp_exchange_string, 'Incompatible options -f and -s'
        blueprint_file = args.blueprint_file[0]
        with open(blueprint_file, 'rt', encoding='ascii') as f:
            for bp_exchange_string in f:
                blueprint_json_str = blueprints.parse_exchange_string(bp_exchange_string.strip())
                process_blueprint_json_string(blueprint_json_str, args)

    return result


if __name__ == "__main__":
    main()
