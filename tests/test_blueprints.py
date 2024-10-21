import blueprints
import unittest


class TestBlueprints(unittest.TestCase):

    def setUp(self):
        self.all_test_files = [ 'tests/examples/blueprint_book.txt',  'tests/examples/oil_processing_1_v1.1.8.txt' ]

    def test_base64_encoding(self):
        for test_file in self.all_test_files:
            with open(test_file, 'r') as fp:
                for blueprint_string in fp:
                    stripped = blueprint_string.strip()

                    json_string = blueprints.parse_bp_exchange_string(stripped)
                    self.assertIsInstance(json_string, str)
                    # print(json_string)

                    base64_string = blueprints.generate_bp_exchange_string(json_string)
                    self.assertIsInstance(base64_string, str)

                    json_string_bis = blueprints.parse_bp_exchange_string(base64_string)
                    self.assertEqual(json_string, json_string_bis)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
