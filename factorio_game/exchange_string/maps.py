#!/usr/bin/env python
"""
Module to parse map exchange strings from the game Factorio (https://www.factorio.com/)

  With good information from: https://wiki.factorio.com/Map_exchange_string_format

  The binary format of the map exchange data was modified multiple times, and to my knowledge there is no exhaustive
  documentation of the different formats. For that reason this script is limited to the most basic parsing.
"""
__author__ = "Pierre DEJOUE"
__copyright__ = "Copyright (c) 2019 Pierre DEJOUE"
__license__ = "MIT License"
__version__ = "0.1"


import base64
import zlib


def parse_exchange_string(map_ex_str: str) -> tuple[bytes, bool]:
    assert len(map_ex_str) >= 6
    assert map_ex_str[0:3] == '>>>'
    assert map_ex_str[-3:] == '<<<'
    map_base64 = map_ex_str[3:-3]
    raw_data = base64.b64decode(map_base64)
    compressed = True
    try:
        map_data = zlib.decompress(raw_data)
    except zlib.error:
        # Uncompressed (the map data was not compressed prior to 0.16)
        compressed = False
        map_data = raw_data
    return map_data, compressed


def parse_game_version(map_bytes: bytes) -> str:
    assert len(map_bytes) >= 8
    version_major = (map_bytes[1] << 8) + map_bytes[0]
    version_minor = (map_bytes[3] << 8) + map_bytes[2]
    version_patch = (map_bytes[5] << 8) + map_bytes[4]
    version_dev   = (map_bytes[7] << 8) + map_bytes[6]
    version_str = f'{version_major}.{version_minor}.{version_patch}'
    if version_dev != 0:
        version_str = f'{version_str}.{version_dev}'
    return version_str
