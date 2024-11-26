import unittest
from io import StringIO
import sys
import json
from config_translator import (
    is_valid_name,
    process_value,
    process_expression,
    evaluate_expression,
    process_dict,
    process_list,
    is_comment,
    process_input,
)

class TestConfigProcessor(unittest.TestCase):
    def test_is_valid_name(self):
        self.assertTrue(is_valid_name("A"))
        self.assertTrue(is_valid_name("ABC"))
        self.assertFalse(is_valid_name("A1"))
        self.assertFalse(is_valid_name("A+B"))
        self.assertFalse(is_valid_name(""))

    def test_is_comment(self):
        self.assertTrue(is_comment("<!-- This is a comment -->"))
        self.assertTrue(is_comment("<!-- Multiline \n comment -->"))
        self.assertFalse(is_comment("Not a comment"))
        self.assertFalse(is_comment("<!-- Missing end"))

    def test_process_value_numeric(self):
        context = {}
        self.assertEqual(process_value(10, context), "10")
        self.assertEqual(process_value(5.5, context), "5.5")

    def test_process_value_string(self):
        context = {"A": 10}
        self.assertEqual(process_value("Hello", context), '"Hello"')
        self.assertEqual(process_value("#[A + 5]", context), "15")
        self.assertIsNone(process_value("<!-- This is a comment -->", context))

    def test_evaluate_expression(self):
        context = {"A": 10, "B": 5}
        self.assertEqual(evaluate_expression("A + B", context), 15)
        self.assertEqual(evaluate_expression("max(A, B)", context), 10)
        self.assertEqual(evaluate_expression("abs(-20)", context), 20)
        with self.assertRaises(ValueError):
            evaluate_expression("A / 0", context)

    def test_process_list(self):
        context = {"A": 10, "B": 5}
        input_list = [1, "#[A + B]", "#[max(A, B)]", "<!-- Comment -->"]
        expected_output = "[1, 15, 10]"
        self.assertEqual(process_list(input_list, context), expected_output)

    def test_process_dict(self):
        context = {"A": 10}
        input_dict = {
            "VALUEONE": "#[A * 2]",
            "COMMENT": "<!-- Ignored -->",
            "VALUETWO": "#[abs(-10)]",
        }
        expected_output = """{
 VALUEONE : 20,
 VALUETWO : 10,
}"""
        self.assertEqual(process_dict(input_dict, context), expected_output)

    def test_process_input(self):
        input_data = {
            "set A": 10,
            "set B": "#[A + 5]",
            "DATA": {
                "VALUEONE": "#[A * 2]",
                "VALUETWO": "#[abs(-10)]"
            },
            "EXTRA": {
                "ITEMS": [1, 2, "#[A + B]"]
            },
            "COMMENT": "<!-- Entire comment -->"
        }
        expected_output = """A = 10;
B = 15;
DATA = {
 VALUEONE : 20,
 VALUETWO : 10,
}
EXTRA = {
 ITEMS : [1, 2, 25],
}
"""
        self.assertEqual(process_input(input_data), expected_output)

    def test_main_with_comments(self):
        # Redirect stdin
        input_json = """{
            "set A": 10,
            "set B": "#[A + 5]",
            "COMMENT": "<!-- Ignored comment -->",
            "DATA": {
                "VALUEONE": "#[A * 2]",
                "VALUETWO": "#[abs(-10)]"
            }
        }"""
        sys.stdin = StringIO(input_json)
        sys.stdout = StringIO()

        # Call main function
        from config_translator import main
        main()

        # Check output file content
        output_file = "output_config.txt"
        with open(output_file, "r") as f:
            output_content = f.read()

        expected_output = """A = 10;
B = 15;
DATA = {
 VALUEONE : 20,
 VALUETWO : 10,
}
"""
        self.assertEqual(output_content.strip(), expected_output.strip())

        # Reset stdin and stdout
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    unittest.main()
