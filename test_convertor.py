import unittest
from convertor import *

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        # Инициализируем тестовые данные
        lines = [
            "keyone: 'value1'",
            "keytwo: 42",
            "keythree: 3.14"
        ]
        self.parser = ConfigParser(lines)


    def test_parse_simple_key_value(self):
        self.parser.parse()
        expected_result = {
            'keyone': 'value1',
            'keytwo': 42,
            'keythree': 3.14
        }
        self.assertEqual(self.parser.config_dict, expected_result)

    def test_parse_array(self):
        lines = [
            "array_key: <<1, 2, 3>>"
        ]
        self.parser = ConfigParser(lines)
        self.parser.parse()
        expected_result = {
            'array_key': ['1', '2', '3']
        }
        self.assertEqual(self.parser.config_dict, expected_result)

    

    def test_parse_with_comments(self):
        lines = [
            "% This is a comment",
            "keyone: 'value1'",
            "{",
            "keytwo: 'value2'",
            "}",
            "keytwo: 3.14"
        ]
        self.parser = ConfigParser(lines)
        self.parser.parse()
        expected_result = {
            'keyone': 'value1',
            'keytwo': 3.14
        }
        self.assertEqual(self.parser.config_dict, expected_result)

    def test_parse_with_calculations(self):
        lines = [
            "value: 10",
            "mix: 20",
            "res: ?[value]"
        ]
        self.parser = ConfigParser(lines)
        self.parser.parse()
        expected_result = {
            'value': 10,
            'mix': 20,
            'res': 10
        }
        self.assertEqual(self.parser.config_dict, expected_result)

    def test_invalid_key_handling(self):
        lines = [
            "key: <<1, 2, 3>>",
            "key: 'new_value'"
        ]
        self.parser = ConfigParser(lines)
        self.parser.parse()
        expected_result = {
            'key': ['1', '2', '3']
        }
        self.assertEqual(self.parser.config_dict, expected_result)

if __name__ == '__main__':
    unittest.main()
