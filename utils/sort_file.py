import os
import re
import string
from utils.decode_any_format import TYPE_TXT_FILE

def sort_and_filter(file_path):
    print(os.getcwd())
    try:
        with open('txt files/'+file_path, 'r', encoding=TYPE_TXT_FILE or 'utf-8') as file:
            lines = file.readlines()
        empty_string_marker = []
        # Фильтрация и удаление строк
        lines = [line.strip().replace('0 - _', '') for line in lines if line.strip() and len(line) >= 30 and bool(re.search(r'[1-9]', line))]

        # Сортировка по первой цифре в строке в убывающем порядке и от 0 до 10
        import re

        sorted_lines = sorted(
            lines,
            key=lambda x: float(re.search(r'\d+(\.\d+)?', x).group()) if re.search(r'\d+(\.\d+)?', x) else 0,
            reverse=True
        )

        # Запись отсортированных строк обратно в файл
        with open('txt files/sorted '+file_path, 'w', encoding=TYPE_TXT_FILE or 'utf-8') as file:
            file.write('\n'.join(sorted_lines))

        print("Файл успешно отсортирован и отфильтрован.")
    except Exception as e:
        with open('txt files/sorted ' + file_path, 'w', encoding=TYPE_TXT_FILE or 'utf-8') as file:
            print(e)
            file.write(f'OmniBot')



