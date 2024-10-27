"""
Unit tests of module factorio_game.exchange_string.maps
"""
import os
import unittest
from factorio_game.exchange_string import maps


class TestMaps(unittest.TestCase):

    def setUp(self):
        self.test_folder = 'tests/examples/maps'
        self.all_test_files =   [ 'old_one.txt', 'my_base.txt', 'forest.txt', 'peninsula_2.0.txt' ]
        self.expected_version = [ '0.10.12',     '0.14.23',     '1.1.110',    '2.0.11.3'          ]

    # maps.parse_exchange_string
    # maps.parse_game_version
    def test_game_version_parsing(self):
        for idx, test_file in enumerate(self.all_test_files):
            test_filepath = os.path.join(self.test_folder, test_file)
            with open(test_filepath, 'r', encoding='ascii') as fp:
                for map_string in fp:
                    stripped = map_string.strip()
                    map_bytes, _ = maps.parse_exchange_string(stripped)
                    self.assertEqual(maps.parse_game_version(map_bytes), self.expected_version[idx])


    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
