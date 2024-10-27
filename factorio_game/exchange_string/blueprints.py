#!/usr/bin/env python
"""
Module to manage blueprint exchange strings from the game Factorio (https://www.factorio.com/)
"""
__author__ = "Pierre DEJOUE"
__copyright__ = "Copyright (c) 2019 Pierre DEJOUE"
__license__ = "MIT License"
__version__ = "0.1"


import base64
import json
import zlib


DEFAULT_EXCHANGE_STRINGS_VERSION = 0


_EXCHANGE_STRINGS_SUPPORTED_VERSIONS = [DEFAULT_EXCHANGE_STRINGS_VERSION]
_ALL_BLUEPRINT_TYPES = {
    'blueprint':              'Blueprint',
    'blueprint_book':         'Blueprint Book',
    'deconstruction_planner': 'Deconstruction Planner',
    'upgrade_planner':        'Upgrade Planner',
}


def _version_check(version: int):
    assert version in _EXCHANGE_STRINGS_SUPPORTED_VERSIONS, 'Blueprint version number ' + str(version) + ' is not among the supported versions: ' + str(_EXCHANGE_STRINGS_SUPPORTED_VERSIONS)


def parse_exchange_string(blueprint_base64: str) -> str:
    version = int(blueprint_base64[0])
    _version_check(version)
    return zlib.decompress(base64.b64decode(blueprint_base64[1:])).decode()


def parse_exchange_string_as_json_object(blueprint_base64: str) -> dict:
    blueprint_json_str = parse_exchange_string(blueprint_base64)
    return json.loads(blueprint_json_str)


def generate_exchange_string(blueprint_raw_string: str, exchange_str_version = DEFAULT_EXCHANGE_STRINGS_VERSION) -> str:
    _version_check(exchange_str_version)
    return str(exchange_str_version) + base64.b64encode(zlib.compress(blueprint_raw_string.encode())).decode()


def generate_exchange_string_from_json_object(blueprint_obj: dict, exchange_str_version = DEFAULT_EXCHANGE_STRINGS_VERSION) -> str:
    # Ensure the most compact JSON format
    json_str = json.dumps(blueprint_obj, sort_keys=True, separators=(',', ':'))
    return generate_exchange_string(json_str, exchange_str_version)


def decode_game_version(version: int):
    version_major = (version & 0x0FFFF000000000000) >> 48
    version_minor = (version & 0x00000FFFF00000000) >> 32
    version_patch = (version & 0x000000000FFFF0000) >> 16
    version_dev   = (version & 0x0000000000000FFFF)
    version_str = f'{version_major}.{version_minor}.{version_patch}'
    if version_dev != 0:
        version_str = f'{version_str}.{version_dev}'
    return version_str


def parse_game_version(blueprint_obj: dict) -> str:
    blueprint_subobj = {}
    for key in _ALL_BLUEPRINT_TYPES:
        if key in blueprint_obj:
            blueprint_subobj = blueprint_obj[key]
    return decode_game_version(blueprint_subobj['version']) if 'version' in blueprint_subobj else 'unknonwn'


def read_blueprint_name(blueprint_obj: dict) -> str:
    blueprint_subobj = {}
    for key in _ALL_BLUEPRINT_TYPES:
        if key in blueprint_obj:
            blueprint_subobj = blueprint_obj[key]
            break
    return blueprint_subobj['label'] if 'label' in blueprint_subobj else 'no-name'


def read_blueprint_type(blueprint_obj: dict) -> str:
    blueprint_type = str(blueprint_obj.keys())
    for key, bp_type in _ALL_BLUEPRINT_TYPES.items():
        if key in blueprint_obj:
            blueprint_type = bp_type
    return blueprint_type
