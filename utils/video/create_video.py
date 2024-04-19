from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.editor import concatenate_videoclips
from random import randint
import ffmpeg
from utils.speech_requests import openai_audio_request
from utils.video.create_translate import create_translate_text
import subprocess
import pysrt
import os
import shutil
from db.database import db
import json


class VideoEditor:
    def __init__(self, user_id, video_title, subtitles, settings):
        db.connect()
        db.is_user_exist(user_id)


        self.settings = settings
        self.video_title = video_title
        self.folder_name = f'{video_title.replace('.mp4','')}'
        self.subtitles = pysrt.open(subtitles)
        self.video = VideoFileClip(self.video_title)
        self.final_fragments = []



    def add_subtitles(self, video_fragment, text):
        subtitle_clip = TextClip(text,  fontsize=int(self.settings['size']), stroke_color=self.settings['outline_color'], stroke_width=self.settings['outline_size'], color=self.settings['color'], font=f"fonts/{self.settings['font']}").set_position(('center', 'bottom')).set_duration(
            video_fragment.duration)
        video_with_subtitles = CompositeVideoClip([video_fragment, subtitle_clip])
        return video_with_subtitles

    def increase_speed(self, video_fragment):
        pass

    def slow_down_speed(self, name, slow_down=0.6):
        command = f'ffmpeg -i {name} -filter:v "setpts=(1/{slow_down})*PTS" -filter:a "atempo={slow_down}" {name.replace("part", "slowed")}'
        subprocess.run(command)
        file_name1 = name
        file_name2 = name.replace("part", "slowed")

        # Получение информации о потоках первого видеофайла
        command = f"ffprobe -v error -show_entries stream=codec_name,codec_type,time_base,start_time,duration,bit_rate,width,height,sample_rate,channel_layout -of json {file_name1}"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        data = json.loads(stdout)

        # Получение параметров видеопотока первого видеофайла
        video_stream = next((stream for stream in data["streams"] if stream["codec_type"] == "video"), None)
        if video_stream is None:
            print("Error: video stream not found")
            exit()
        video_codec = video_stream["codec_name"]
        video_time_base = video_stream["time_base"]
        video_start_time = video_stream["start_time"]
        video_duration = video_stream["duration"]
        video_bit_rate = video_stream["bit_rate"]
        video_width = video_stream["width"]
        video_height = video_stream["height"]

        # Получение параметров аудиопотока первого видеофайла
        audio_stream = next((stream for stream in data["streams"] if stream["codec_type"] == "audio"), None)
        if audio_stream is None:
            print("Error: audio stream not found")
            exit()
        audio_codec = audio_stream["codec_name"]
        audio_time_base = audio_stream["time_base"]
        audio_start_time = audio_stream["start_time"]
        audio_duration = audio_stream["duration"]
        audio_bit_rate = audio_stream["bit_rate"]
        audio_sample_rate = audio_stream["sample_rate"]
        audio_channel_layout = audio_stream["channel_layout"]

        # Создание команды ffmpeg для изменения параметров второго видеофайла
        command = f"ffmpeg -i {file_name2} -c:v {video_codec} -b:v {video_bit_rate} -s {video_width}x{video_height} -r 25 -c:a {audio_codec} -b:a {audio_bit_rate} -ar {audio_sample_rate} -ac 2 {file_name2.replace('.mp4', '_changed.mp4')}"

        # Выполнение команды ffmpeg
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error: {stderr.decode()}")
        else:
            print(f"Video parameters changed successfully: {file_name2.replace('.mp4', '_changed.mp4')}")

        os.remove(name.replace("part", "slowed"))
        os.remove(name)
        os.rename(file_name2.replace('.mp4', '_changed.mp4'), name)
        return name


    def create_folder(self):
        if os.path.exists(self.folder_name):
            shutil.rmtree(self.folder_name)
        os.makedirs(self.folder_name)

    def add_timestamps(self, timestamp1, timestamp2):
        # Преобразуем временные метки в секунды
        h, m, s = map(float, timestamp1.split(':'))
        total_seconds1 = h * 3600 + m * 60 + s

        s, ms = map(float, timestamp2.split('.'))
        total_seconds2 = s + ms / 1000

        # Складываем временные метки
        total_seconds = total_seconds1 + total_seconds2

        # Преобразуем результат обратно в формат временной метки
        h = int(total_seconds // 3600)
        m = int(total_seconds % 3600 // 60)
        s = int(total_seconds % 60)
        ms = int((total_seconds - int(total_seconds)) * 1000)

        # Добавляем ведущие нули, если необходимо
        h = f'0{h}' if h < 10 else h
        m = f'0{m}' if m < 10 else m
        s = f'0{s}' if s < 10 else s
        ms = f'0{ms}' if ms < 100 else f'00{ms}' if ms < 10 else ms

        # Возвращаем результат в формате временной метки
        return f'{h}:{m}:{s}.{ms}'

    def create_original_chunk(self, start, end, text, translated_text, output_file):
        if self.settings['original_speed'] != 1:
            print(self.settings['original_speed'])
            original_fragment = self.slow_down_speed(output_file, self.settings['original_speed'])

        original_fragment = self.video.subclip(start, end)
        if self.settings['subtitles']:
            original_fragment = self.add_subtitles(original_fragment, text=text + '\n' + translated_text)
        original_fragment.write_videofile(output_file)
        original_fragment.close()



    def create_translated_chunk(self, start, text, translated_text, number, end, idx, output_file):
        audio_path = f"{self.folder_name}/translated_part{number}.mp3"

        answer = openai_audio_request(model="tts-1", voice=self.settings['synthes_voice'], input_text=translated_text,
                                      output_file=audio_path, speed=self.settings['synthes_speed'])

        translated_speech = AudioFileClip(audio_path)
        duration_yandex_speech = str(float(translated_speech.duration)+0.3)
        print(duration_yandex_speech, 'СКОРОСТЬ ПЕРЕВОДА АУДИО')

        end_time = self.add_timestamps(start, duration_yandex_speech)


        if end_time > end:
            print(end_time, end)
            end_time = end

        translated_fragment = self.video.subclip(start, end_time)

        translated_fragment = translated_fragment.set_audio(translated_speech)
        if self.settings['subtitles']:
            translated_fragment = self.add_subtitles(translated_fragment, text=text + '\n' + translated_text)

        translated_fragment.write_videofile(output_file)
        translated_fragment.close()
        os.remove(audio_path)

    def edit_video(self):
        self.create_folder()

        final_fragments = []
        for idx, n in enumerate(self.subtitles):
            start, end = str(n.start).replace(',', '.'), str(n.end).replace(',', '.')
            text = n.text
            if idx != len(self.subtitles) - 1 and start!=end:
                if self.settings['translator']:
                    translated_text = create_translate_text(text)
                    output_file_translated = f"{self.folder_name}/translated_part{idx}.mp4"
                    self.create_translated_chunk(start, text, translated_text, idx, end, idx, output_file_translated)
                    final_fragments.append(output_file_translated)
                else:
                    translated_text = ''

                output_file_original = f"{self.folder_name}/original_part{idx}.mp4"
                self.create_original_chunk(start, end, text, translated_text, output_file_original)
                final_fragments.append(output_file_original)

        with open(f'{self.folder_name}/files.txt', 'w') as f:
            # Проходим по всем файлам и добавляем их пути в файл
            for file in final_fragments:
                f.write('file {}\n'.format(file.split('/')[2]))
        subprocess.run(f'ffmpeg -f concat -i {self.folder_name}/files.txt -c copy {self.folder_name}/ready.mp4')
        self.video.close()

        return f'{self.folder_name}/ready.mp4'


def combine_video_chunks(files, title):
    tmp_video_path = "TmpVideo"
    print(files)
    with open(f'{tmp_video_path}/files.txt', 'w') as f:
        # Проходим по всем файлам и добавляем их пути в файл
        for file in files:
            print('fileee', file.split('o/')[1])
            f.write('file {}\n'.format(file.split('o/')[1]))

    subprocess.run(f'ffmpeg -f concat -i {tmp_video_path}/files.txt -c copy video/omni_{title}.mp4')

    return f'video/omni_{title}.mp4'





