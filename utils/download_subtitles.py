import pytube
from pytube import Playlist, YouTube
import os
import xml.etree.ElementTree as ET
import re
from spawnbot import bot
from aiogram.types.input_file import FSInputFile
import concurrent.futures

def all_files_in_one():
    folder_path = 'subtitles'

    output_file = open('объединенный_файл.txt', 'w', encoding='utf-8')
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                output_file.write(file.read())
                output_file.write('\n')

    output_file.close()
    print('Файлы успешно объединены в один файл.')


def extract_subtitles(name):
    tree = ET.parse(f'./subtitles/{name}.xml')
    root = tree.getroot()

    phrases = []
    p_tags = root.findall(".//p")

    head_tag = root.find(".//head")

    if head_tag is not None:
        p_tags = p_tags[::2]

    for i, p_tag in enumerate(p_tags):
        phrase_info = {}

        phrase_info["subtitle_number"] = len(phrases) + 1
        phrase_info["start_time"] = int(p_tag.get("t", 0))
        phrase_info["end_time"] = phrase_info["start_time"] + int(p_tag.get("d", 0))

        words = p_tag.findall(".//s")
        if words:
            phrase_info["text"] = " ".join(word.text.strip() for word in words)
        else:
            phrase_info["text"] = p_tag.text.strip()

        if i + 1 < len(p_tags):
            next_p_tag = p_tags[i + 1]
            phrase_info["next_start_time"] = int(next_p_tag.get("t", 0))

        phrases.append(phrase_info)

    return phrases

def format_time(milliseconds: int) -> str:
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds %= 60
    return f'{minutes:02d}:{seconds:02d}'


def download_video_subtitles(url_video, _all_=False):
    yt = YouTube(url_video)
    title = None
    try:
        video_stream = yt.streams.get_highest_resolution()
        available_captions = yt.captions.all()
        print(yt.captions)
        selected_caption = None
        for caption in available_captions:
            if caption.code == 'ru':
                selected_caption = caption
                break
            selected_caption = caption
        title = re.sub(r'[^\w\sа-яёА-ЯЁ]', '', yt.title).replace(' ', '_')
        if _all_:
            if selected_caption:
                with open(f'subtitles/{title}.xml', 'w', encoding='utf-8') as f:
                    f.write(selected_caption.xml_captions)
                for i in (extract_subtitles(title)):
                    with open(f'subtitles/{title}.txt', 'a', encoding='utf-8') as f:
                        f.write(str(format_time(i['start_time'])) + '->' + str(format_time(i['end_time'])) + '\n')
                        f.write(i['text'] + '\n')


        else:
            if selected_caption:
                with open(f'subtitles/{title}.xml', 'w', encoding='utf-8') as f:
                    f.write(selected_caption.xml_captions)
                for i in (extract_subtitles(title)):
                    with open(f'subtitles/{title}.txt', 'a', encoding='utf-8') as f:
                        f.write(i['text']+'\n')

    except Exception as e:
        print(e)
    return title

async def _update_progress(answers, chunks, message, msg):
    try:
        new_text = f'<b>Процесс работы:</b> <i>{len(answers)}/{len(chunks)}</i>'
        if msg.text != new_text:
            await bot.edit_message_text(new_text,
                                         chat_id=message.from_user.id,
                                         message_id=msg.message_id)
    except Exception as e:
        print(e)

async def download_playlist_subtitles(url_playlist, c_id, message):

    link = Playlist(url_playlist)
    names = []
    print(link)
    await bot.send_message(c_id, f'Количество видео в плейлисте: {len(link.video_urls)}')
    msg = await message.answer(f'<b>Процесс работы:</b> <i>0/{len(link.video_urls)}</i>')
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        future = [executor.submit(download_video_subtitles, url) for url in link.video_urls]
        for future in concurrent.futures.as_completed(future):
            names.append(str(future.result()))
            await _update_progress(names,link.video_urls, message , msg)
    return names