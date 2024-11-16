import re

subtitles_files = [f'sub{i}.ru.srt' for i in range(0, 610)]
output_file = 'subtitles/combined_subtitles.txt'
with open(output_file, 'w', encoding='utf-8') as outfile:
    for input_file in subtitles_files:
        try:
            with open(input_file, 'r', encoding='utf-8') as infile:
                for line in infile:
                    # Удаляем строки с таймкодами и номера субтитров
                    if re.match(r'^\d+$', line) or re.match(r'^\d{2}:\d{2}:\d{2},\d{3} -->', line):
                        continue
                    # Удаляем HTML-теги
                    clean_line = re.sub(r'<[^>]*>', '', line).strip()
                    if clean_line:  # Записываем только не пустые строки
                        outfile.write(clean_line + '\n')
        except:
            ...

print(subtitles_files)