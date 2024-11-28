a = 'Kevin Hart: Will Ferrell Is “Cheap As Hell" | CONAN on TBS'
import re

# Замена всех символов, кроме русских, английских букв, цифр, '/', '\' и '.', на '_'
sanitized_video_path = re.sub(r"[^A-Za-zА-Яа-я0-9/\\\.]", "_", a)

print(sanitized_video_path)