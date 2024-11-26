import sys
import json
import re

def is_valid_name(name):
    return bool(re.match(r'^[A-Z]+$', name))

def process_value(value, context=None):
    if isinstance(value, dict):
        return process_dict(value, context)
    elif isinstance(value, list):
        return process_list(value, context)
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if is_comment(value):  
            return None
        return process_expression(value, context) 
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")

def is_comment(value):
    return value.strip().startswith("<!--") and value.strip().endswith("-->")

def process_expression(value, context):
    if value.startswith('#[') and value.endswith(']'):
        expression = value[2:-1].strip()
        result = evaluate_expression(expression, context)
        return str(result)
    return f'"{value}"'  # Обрабатываем строку, если нет выражения

def evaluate_expression(expression, context):
    try:
        allowed_functions = {'abs': abs, 'max': max, 'min': min, 'round': round}
        
        for var in context:
            expression = re.sub(rf'\b{var}\b', str(context[var]), expression)
        
        return eval(expression, {"__builtins__": None}, allowed_functions)
    except Exception as e:
        raise ValueError(f"Ошибка при вычислении выражения '{expression}': {e}")

def process_dict(d, context):
    result = '{\n'
    for key, value in d.items():
        if isinstance(key, str) and is_comment(key):  # Пропускаем комментарии в ключах
            continue
        if isinstance(value, str) and is_comment(value):  # Пропускаем комментарии в значениях
            continue
        if not is_valid_name(key):
            raise ValueError(f"Invalid name '{key}'")
        processed_value = process_value(value, context)
        if processed_value is not None:  # Пропускаем пустые значения
            result += f' {key} : {processed_value},\n'
    result += '}'
    return result

def process_list(value, context):
    processed_items = [
        process_value(v, context)
        for v in value
        if not (isinstance(v, str) and is_comment(v))  # Пропускаем комментарии
    ]
    return f'[{", ".join(filter(None, processed_items))}]'

def process_input(data):
    result = ""
    context = {}  # Создаем контекст для хранения значений переменных

    for key, value in data.items():
        if isinstance(key, str) and is_comment(key):  # Пропускаем комментарии в ключах
            continue
        if isinstance(value, str) and is_comment(value):  # Пропускаем комментарии в значениях
            continue
        if key.startswith('set '):
            const_name = key[4:].strip()  # Убираем префикс 'set ' и пробелы
            if not is_valid_name(const_name):
                raise ValueError(f"Invalid constant name '{const_name}'")
            context[const_name] = process_value(value, context)
            result += f"{const_name} = {context[const_name]};\n"
        elif isinstance(value, dict):
            result += f"{key} = {process_dict(value, context)}\n"
        else:
            processed_value = process_value(value, context)
            if processed_value is not None:
                result += f"{key} = {processed_value}\n"
    return result

def main():
    try:
        input_data = sys.stdin.read()

        data = json.loads(input_data)

        output = process_input(data)

        output_filename = "output_config.txt"
        with open(output_filename, 'w') as file:
            file.write(output)

        print(f"Конфигурация успешно записана в файл: {output_filename}")

    except json.JSONDecodeError:
        sys.stderr.write("Ошибка: Неверный формат JSON. Убедитесь, что JSON корректен.\n")
    except ValueError as e:
        sys.stderr.write(f"Ошибка: {e}\n")
    except Exception as e:
        sys.stderr.write(f"Ошибка: {e}\n")


if __name__ == "__main__":
    main()
