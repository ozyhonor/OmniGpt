import subprocess

# Команда yt-dlp
yt_dlp_command = [
    "yt-dlp",
    "--skip-download",
    "--write-subs",
    "--cookies",
    "cookies.txt",
    "--write-auto-subs",
    "--sub-lang", "ru",
    "--sub-format", "ttml",
    "--convert-subs", "srt",
    "--proxy", "http://aVD2fd:PKwhr7@94.131.88.53:9601",
    "--output", "transcript.%(ext)s",
    "https://youtu.be/24WdzeGcbOI?si=HlfeL38TMURxnLOW"
]

# Запускаем yt-dlp
subprocess.run(yt_dlp_command, check=True)

# Команда sed для обработки файла transcript.en.srt
sed_command_1 = [
    "sed",
    "-i", "",
    "-e", "/^[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]$/d",
    "-e", "/^[[:digit:]]\\{1,3\\}$/d",
    "-e", "s/<[^>]*>//g",
    "./transcript.en.srt"
]

subprocess.run(sed_command_1, check=True)

# Второй этап обработки файла с помощью sed
sed_command_2 = [
    "sed",
    "-e", "s/<[^>]*>//g",
    "-e", "/^[[:space:]]*$/d",
    "transcript.en.srt",
    ">", "output.txt"
]

# Выполняем вторую команду sed
subprocess.run(" ".join(sed_command_2), shell=True, check=True)

# Удаляем временный файл transcript.en.srt
rm_command = ["rm", "transcript.en.srt"]
subprocess.run(rm_command, check=True)
