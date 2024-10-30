def time_to_float(time_str):
    # Заменяем запятую на точку, чтобы обработать оба формата
    time_str = time_str.replace(",", ".")
    # Разделяем на часы, минуты и секунды
    hours, minutes, seconds = time_str.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

# Примеры
start = "0:00:00"
end1 = "0:00:03.440000"
end2 = "00:00:24,159"

# Переводим в float
start_seconds = time_to_float(start)
end_seconds1 = time_to_float(end1)
end_seconds2 = time_to_float(end2)

# Сравнения
print("Сравнение end1 и start:")
if end_seconds1 > start_seconds:
    print("end1 больше start")
else:
    print("start больше или равно end1")

print("\nСравнение end2 и start:")
if end_seconds2 > start_seconds:
    print("end2 больше start")
else:
    print("start больше или равно end2")

# Вывод значений
print(f"\nНачальное время: {start_seconds} сек")
print(f"Конечное время end1: {end_seconds1} сек")
print(f"Конечное время end2: {end_seconds2} сек")
