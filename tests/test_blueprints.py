import blueprints
import unittest


class TestBlueprints(unittest.TestCase):


    def setUp(self):
        self.all_test_files = [ 'tests/examples/blueprint_book.txt' ]


    def test_base64_encoding(self):
        for test_file in self.all_test_files:
            try:
                fp = open(test_file, 'r')
                for blueprint_string in fp:
                    stripped = blueprint_string.strip()

                    json_string = blueprints.parse_blueprint_string(stripped)
                    self.assertIsInstance(json_string, str)
                    print(json_string)

                    base64_string = blueprints.generate_blueprint_string(json_string)
                    self.assertIsInstance(base64_string, str)

                    json_string_bis = blueprints.parse_blueprint_string(base64_string)
                    self.assertEqual(json_string, json_string_bis)
            finally:
                fp.close()


    def test_db_filename(self):
        name = "foo"
        for idx in [-1, 0, 1, 10, 100, 1000]:
            filename = blueprints.generate_blueprint_filename(name, idx)
            parsed = blueprints.parse_blueprint_filename(filename)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed['name'], name)
            self.assertEqual(parsed['index'], idx)
            self.assertEqual(parsed['filename'], filename)


    def tearDown(self):
        pass




if __name__ == '__main__':
    unittest.main()
