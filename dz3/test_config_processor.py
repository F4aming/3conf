import unittest
import json
import os
from io import StringIO
from unittest.mock import patch
from config_translator import (
    is_valid_name,
    process_value,
    process_dict,
    process_list,
    process_input,
    write_to_file,
)


class TestConfigProcessor(unittest.TestCase):
    
    # Тест для проверки валидности имени
    def test_is_valid_name(self):
        self.assertTrue(is_valid_name("VALID_NAME"))
        self.assertTrue(is_valid_name("ANOTHER_NAME"))
        self.assertFalse(is_valid_name("InvalidName"))
        self.assertFalse(is_valid_name("INVALID-NAME"))
        self.assertFalse(is_valid_name("123INVALID"))

    # Тест для проверки обработки чисел и строк
    def test_process_value(self):
        self.assertEqual(process_value(123), "123")
        self.assertEqual(process_value(45.67), "45.67")
        self.assertEqual(process_value("test"), '"test"')
        self.assertEqual(process_value([1, 2, 3]), '[1, 2, 3]')
        self.assertEqual(process_value({"KEY": "value"}), '{\n KEY : "value",\n}')
        
        with self.assertRaises(ValueError):
            process_value(set([1, 2, 3]))  # Неподдерживаемый тип данных

    # Тест для проверки обработки словаря
    def test_process_dict(self):
        input_dict = {"KEY": "value", "NUMBER": 42}
        expected_output = '{\n KEY : "value",\n NUMBER : 42,\n}'
        self.assertEqual(process_dict(input_dict), expected_output)
        
        # Тест на невалидный ключ
        with self.assertRaises(ValueError):
            process_dict({"Invalid-Name": "value"})

    # Тест для проверки обработки списков
    def test_process_list(self):
        input_list = [1, "string", {"KEY": "value"}]
        expected_output = '[1, "string", {\n KEY : "value",\n}]'
        self.assertEqual(process_list(input_list), expected_output)

    # Тест для проверки обработки ввода
    def test_process_input(self):
        input_data = {
            "set_VARIABLE": 123,
            "CONFIG": {"KEY_ONE": "value1", "KEY_TWO": [1, 2, 3]},
            "LIST": ["one", "two"],
        }
        expected_output = (
            "set VARIABLE = 123;\n"
            "CONFIG = {\n KEY_ONE : \"value1\",\n KEY_TWO : [1, 2, 3],\n}\n"
            "LIST = [\"one\", \"two\"]\n"
        )
        self.assertEqual(process_input(input_data), expected_output)

    # Тест для проверки записи в файл
    def test_write_to_file(self):
        output = "set VARIABLE = 123;\nCONFIG = { KEY : \"value\" }\n"
        filename = "test_output.txt"
        
        # Записываем в файл
        write_to_file(output, filename)
        
        # Проверяем, что файл создан и содержит правильные данные
        self.assertTrue(os.path.exists(filename))
        with open(filename, 'r') as file:
            file_content = file.read()
        self.assertEqual(file_content, output)
        
        # Удаляем файл после теста
        os.remove(filename)

    # Тест для проверки обработки ввода из stdin
    @patch('sys.stdin', StringIO('{"set_TEST": 100, "ITEMS": ["item1", "item2"]}'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_main(self, mock_stdout):
        from config_translator import main
        main()
        output_filename = 'output_config.txt'
        
        # Проверка корректности вывода в файл
        self.assertTrue(os.path.exists(output_filename))
        with open(output_filename, 'r') as file:
            file_content = file.read()
        
        expected_output = 'set TEST = 100;\nITEMS = ["item1", "item2"]\n'
        self.assertEqual(file_content, expected_output)
        
        # Проверка вывода на консоль
        self.assertIn("Конфигурация записана в файл", mock_stdout.getvalue())
        
        # Удаляем файл после теста
        os.remove(output_filename)


if __name__ == "__main__":
    unittest.main()
