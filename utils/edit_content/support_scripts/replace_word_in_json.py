import json
import asyncio

async def process_json(file):
    # Открытие исходного JSON файла
    with open(file, 'r') as f:
        a = json.loads(f.read())

    # Разделяем текст на слова
    w1 = [i for i in a['text'].split()]

    # Обрабатываем слова с дефисами и разделяем их на отдельные слова
    for i in w1:
        if ('.' in i) and not i.endswith('.') and i.count('.')==1:
            index = w1.index(i)
            w1[index] = i.split('.')[0]
            for _ in i.split('.')[1:]:
                w1.insert(index + 1, _)
        if (',' in i) and not i.endswith(','):
            index = w1.index(i)
            w1[index] = i.split(',')[0]
            for _ in i.split(',')[1:]:
                w1.insert(index + 1, _)
        if '-' in i:
            index = w1.index(i)
            w1[index] = i.split('-')[0]
            for _ in i.split('-')[1:]:
                w1.insert(index + 1, _)
        if '%' in i:
            index = w1.index(i)
            w1[index] = i.split('%')[0]
            for _ in i.split('%')[1:]:
                w1.insert(index + 1, _)

        if i.count('.') >= 2:
            index = w1.index(i)
            parts = i.split('.')
            w1[index] = parts[0]  # Первое слово + точка
            for part in parts[1:]:
                if part:
                    print(part, 'paaart')  # Игнорируем пустые строки
                    w1.insert(index + 1, part)

    # Получаем список слов из исходной структуры JSON
    w2 = [i["word"] for i in a['words']]
    for a,i in enumerate(w2):
        print(i, w1[a])

    # Заменяем слова в w2 на обновленные из w1
    for i in range(len(a['words'])):
        a['words'][i]["word"] = w1[i]  # Присваиваем обновленное слово из w1 в w2

    # Если w1 и w2 не равны, выводим их
    if len(w1) != len(w2):
        print("w1 и w2 не равны!")
        print("w1:", w1)
        print("w2:", w2)
        return
    print("w1:", w1)
    print("w2:", w2)
    # Записываем изменения обратно в JSON файл
    with open(file, 'w') as f:
        json.dump(a, f, indent=4)
