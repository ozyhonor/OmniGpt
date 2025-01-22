from moviepy import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy import concatenate_videoclips
from random import randint
from utils.speech_requests import openai_audio_request
from utils.edit_content.create_translate import create_translate_text
import subprocess
import pysrt
import os
import shutil
from db.database import db
import json
from moviepy.video.tools.subtitles import SubtitlesClip


class VideoEditor:
    def __init__(self, user_id, video_title, subtitles, settings):
        db.connect()
        db.is_user_exist(user_id)

        self.user_id = user_id
        self.settings = settings
        self.video_title = video_title
        self.folder_name = f'{video_title.replace('.mp4','')}'
        self.subtitles = pysrt.open(subtitles)
        self.subtitles_path = subtitles
        self.video = VideoFileClip(self.video_title)
        self.final_fragments = []

    def split_string(self, input_string, max_length=32):
        parts = input_string.split('\n')
        result = []

        for part in parts:
            words = part.split()
            lines = []
            current_line = ""

            for word in words:
                if len(current_line) + len(word) + 1 > max_length:
                    lines.append(current_line)
                    current_line = word
                else:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word

            if current_line:
                lines.append(current_line)

            result.append("\n".join(lines))

        return "\n".join(result)


    def add_subtitles(self, video_fragment, text):
        subtitle_clip = TextClip(self.split_string(text), bg_color=self.settings['shadow_color'],  fontsize=int(self.settings['size']), stroke_color=self.settings['outline_color'], stroke_width=self.settings['outline_size'], color=self.settings['color'], font=f"fonts/{self.settings['font']}").set_position(('center', 'bottom')).set_duration(
            video_fragment.duration)
        video_with_subtitles = CompositeVideoClip([video_fragment, subtitle_clip])
        return video_with_subtitles

    def increase_speed(self, video_fragment):
        pass


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

    def create_original_chunk(self, start, end, text, translated_text, output_file, only_sub=False):
        original_fragment = self.video.subclip(start, end)
        if self.settings['subtitles']:
            original_fragment = self.add_subtitles(original_fragment, text=text + '\n' + translated_text)
        if self.settings['translator']:
            original_fragment.write_videofile(output_file)
        else:
            original_fragment = self.add_subtitles(original_fragment, text=text + '\n' + translated_text)
            self.final_fragments.append(original_fragment)

        original_fragment.close()



    def create_translated_chunk(self, start, text, translated_text, number, end, idx, output_file):
        audio_path = f"{self.folder_name}/translated_part{number}.mp3"

        answer = openai_audio_request(model="tts-1", voice=self.settings['synthes_voice'], input_text=translated_text,
                                      output_file=audio_path, speed=self.settings['translation_speed'])

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

    def convert_time_to_timecode(self, time_str1, time_str2):
        time_str = time_str1[0:len(time_str1) - 1].split('.')
        a = time_str[0].split(':')
        h = int(a[0]) * 24 * 60 + int(a[1]) * 60 + int(a[2])
        start = (str(h) + '.' + time_str[1])

        time_str = time_str2[0:len(time_str2) - 1].split('.')
        a = time_str[0].split(':')
        h = int(a[0]) * 24 * 60 + int(a[1]) * 60 + int(a[2])
        end = (str(h) + '.' + time_str[1])

        return float(end)-float(start)


    def edit_video(self):
        self.create_folder()
        if self.settings['translator']:
            final_fragments = []
            for idx, n in enumerate(self.subtitles):
                start, end = str(n.start).replace(',', '.'), str(n.end).replace(',', '.')
                text = n.text
                if idx != len(self.subtitles) - 1 and start!=end:
                    if self.settings['translator']:
                        translated_text = create_translate_text(text, self.settings['translated_language'])
                        output_file_translated = f"{self.folder_name}/translated_part{idx}.mp4"
                        self.create_translated_chunk(start, text, translated_text, idx, end, idx, output_file_translated)
                        final_fragments.append(output_file_translated)
                    else:
                        translated_text = ''

                    output_file_original = f"{self.folder_name}/original_part{idx}.mp4"

                    a = self.create_original_chunk(start, end, text, translated_text, output_file_original,
                                                   only_sub=db.get_user_settings('translator', self.user_id))
                    if self.settings['translator']:
                        final_fragments.append(output_file_original)
                    else:
                        final_fragments.append(a)
            with open(f'{self.folder_name}/files.txt', 'w') as f:
                # Проходим по всем файлам и добавляем их пути в файл
                for file in final_fragments:
                    f.write('file {}\n'.format(file.split('/')[2]))

            cmd = ["ffmpeg", "-y", "-f", "concat", "-i", f"{self.folder_name}/files.txt", "-c", "copy", f"{self.folder_name}/ready.mp4"]
            subprocess.run(cmd)
            self.video.close()
        else:
            generator = lambda text: TextClip(text, fontsize=int(self.settings['size']),
                                     stroke_color=self.settings['outline_color'],
                                     bg_color=self.settings['shadow_color'],
                                     stroke_width=self.settings['outline_size'], color=self.settings['color'],
                                     font=f"fonts/{self.settings['font']}")
            subs = SubtitlesClip(self.subtitles_path, generator)
            subtitles = SubtitlesClip(subs, generator)

            result = CompositeVideoClip([self.video, subtitles.set_position(('center', 'bottom'))])

            result.write_videofile(F'{self.folder_name}/ready.mp4')


        return f'{self.folder_name}/ready.mp4'


def combine_video_chunks(files, title):
    tmp_video_path = "TmpVideo"
    print(files)
    with open(f'{tmp_video_path}/files.txt', 'w') as f:
        # Проходим по всем файлам и добавляем их пути в файл
        for file in files:
            print('fileee', file.split('o/')[1])
            f.write('file {}\n'.format(file.split('o/')[1]))

    command = ["ffmpeg",
               "-y",
               "-f",
               "concat",
               "-i",
               f"{tmp_video_path}/files.txt",
               "-c",
               "copy",
               f"video/omni_{title}"]
    subprocess.run(command)

    return f'video/omni_{title}'





