"""
Unit tests of module factorio_game.exchange_string.blueprints
"""
import os
import unittest
from factorio_game.exchange_string import blueprints


class TestBlueprints(unittest.TestCase):

    def setUp(self):
        self.test_folder = 'tests/examples/blueprints'
        self.all_test_files =   [ 'blueprint_book.txt', 'oil_processing_1_v1.1.8.txt',   'decon_planner.txt',      'red_circuits_block.txt' ]
        self.expected_version = [ '0.17.9.1',           '1.1.8',                         '1.1.107',                '2.0.11.3'               ]
        self.expected_name =    [ 'My Book',            'Crude Oil Processing - step 1', 'Coal Rocks',             'Red Circuits Block'     ]
        self.expected_type =    [ 'Blueprint Book',     'Blueprint',                     'Deconstruction Planner', 'Blueprint'              ]

    # blueprints.parse_exchange_string
    # blueprints.generate_exchange_string
    def test_base64_encoding_and_decoding(self):
        for test_file in self.all_test_files:
            test_filepath = os.path.join(self.test_folder, test_file)
            with open(test_filepath, 'r', encoding='ascii') as fp:
                for blueprint_string in fp:
                    stripped = blueprint_string.strip()

                    json_string = blueprints.parse_exchange_string(stripped)
                    self.assertIsInstance(json_string, str)

                    base64_string = blueprints.generate_exchange_string(json_string)
                    self.assertIsInstance(base64_string, str)

                    json_string_bis = blueprints.parse_exchange_string(base64_string)
                    self.assertEqual(json_string, json_string_bis)

    # blueprints.decode_game_version
    def test_game_version_decoding(self):
        self.assertEqual(blueprints.decode_game_version(281479278886912), '1.1.110')

    # blueprints.parse_exchange_string_as_json_object
    # blueprints.parse_game_version
    def test_game_version_parsing(self):
        for idx, test_file in enumerate(self.all_test_files):
            test_filepath = os.path.join(self.test_folder, test_file)
            with open(test_filepath, 'r', encoding='ascii') as fp:
                for blueprint_string in fp:
                    stripped = blueprint_string.strip()
                    json_obj = blueprints.parse_exchange_string_as_json_object(stripped)
                    self.assertEqual(blueprints.parse_game_version(json_obj), self.expected_version[idx])

    # blueprints.parse_exchange_string_as_json_object
    # blueprints.read_blueprint_name
    def test_blueprint_name_parsing(self):
        for idx, test_file in enumerate(self.all_test_files):
            test_filepath = os.path.join(self.test_folder, test_file)
            with open(test_filepath, 'r', encoding='ascii') as fp:
                for blueprint_string in fp:
                    stripped = blueprint_string.strip()
                    json_obj = blueprints.parse_exchange_string_as_json_object(stripped)
                    self.assertEqual(blueprints.read_blueprint_name(json_obj), self.expected_name[idx])

    # blueprints.parse_exchange_string_as_json_object
    # blueprints.read_blueprint_type
    def test_blueprint_type_parsing(self):
        for idx, test_file in enumerate(self.all_test_files):
            test_filepath = os.path.join(self.test_folder, test_file)
            with open(test_filepath, 'r', encoding='ascii') as fp:
                for blueprint_string in fp:
                    stripped = blueprint_string.strip()
                    json_obj = blueprints.parse_exchange_string_as_json_object(stripped)
                    self.assertEqual(blueprints.read_blueprint_type(json_obj), self.expected_type[idx])


    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
