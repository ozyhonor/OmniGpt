from spawnbot import bot
from aiogram import Router, F
from  db.database import db
from aiogram.types import Message
from states.states import WaitingStateDoVideo
from aiogram.fsm.context import FSMContext
from utils.video.split_video_audio import split_video_and_get_subtitles
from menu.keyboards import CustomKeyboard
from utils.create_download_link import upload_to_fileio
import os
from utils.video.slow_down_speed import slow_down_speed
from aiogram.types.input_file import FSInputFile
import shutil
from utils.youtube_downloaders.download_video import download_video_from_youtube
from utils.check_interesting_moment import choose_good_moment
from utils.video.clear_directory import clear_directory
from utils.video.check_size import check_size
from utils.video.convert_to_short_resol import change_resolution_video
from utils.download_from_googledrive import create_and_upload_file
from utils.video.create_video import VideoEditor, combine_video_chunks
from utils.video.split_video import split_timestamps
from utils.video.add_music import add_music
from utils.video.video_editor import process_video
from utils.download_subtitles import download_video_subtitles
from utils.gpt_requests import file_request
from utils.split_text_for_gpt import split_text
from utils.decode_any_format import detect_file_format
from menu import texts

video_editor_router = Router()


@video_editor_router.message(F.text == '🛠️ Создать видео')
async def create_video_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается youtube ссылка или файл формата mp4.', reply_markup=markup)
    await state.set_state(WaitingStateDoVideo.do_video)


@video_editor_router.message(WaitingStateDoVideo.do_video)
async def process_video_handler(message: Message, state: FSMContext):
    '''
    скачать
    обоаботать
    отдать
    '''
    user_id = message.from_user.id
    url_video = message.text

    #Скачать
    await message.answer('Скачиваю видео...')
    video_path = await download_video_from_youtube(url_video, user_id)

    #Обработать
    await message.answer('Обрабатываю видео')
    await process_video(video_path, user_id)

    trusted_fragments = []
    settings = db.get_all_user_settings(user_id)
    markup = CustomKeyboard.inline_shadow_color()
    time_crop = db.get_timestamps(user_id)
    print(time_crop)
    smart = db.get_smart_sub(user_id)
    if db.get_original_speed(user_id) != 1:
        slow_down_speed('video/'+video_path, slow_down=db.get_original_speed(user_id))

    print(video_path)
    for i,timestamp in enumerate(time_crop.split(' ')):
        if time_crop != '0':
            splited_timestamps = split_timestamps(timestamp.split('-'), 'video/'+video_path)
        else:splited_timestamps = False
        split_video_and_get_subtitles(smart, splited_timestamps or 'video/'+video_path, 'TmpVideo',16, settings['max_words'], overlap=settings['overlap'])
        files = ([i for i in os.listdir('TmpVideo') if i.endswith('.mp4') and '_' in i])
        files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        ready_files = []
        for file in files:
            if trusted_fragments!=[]:
                await message.answer(trusted_fragments[i]['name'] + trusted_fragments[i]['tags'])
            else:
                await message.answer('Обработка видео...')
            ready_files.append(VideoEditor(
                settings=settings,
                subtitles=f'TmpVideo/{file.replace('.mp4','.srt')}',
                video_title=f'TmpVideo/{file}',
                user_id=user_id
            ).edit_video())
        if len(files) == 1:
            source_path = "TmpVideo/piece_0/ready.mp4"
            target_path = "video"
            new_name = "omni_{title}"
            shutil.move(source_path, target_path)
            moved_file = os.path.join(target_path, "ready.mp4")
            os.rename(moved_file, os.path.join(target_path, new_name.format(title=video_path)))
        else:
            combine_video_chunks(ready_files, video_path)
        db.connect()
        if db.get_resolution(user_id) != 'original':
            change_resolution_video(title=f'video/omni_{video_path}')
        if db.get_user_settings('music', user_id) != 'None':
            music = db.get_user_settings('music', user_id)
            music_volume = db.get_user_settings('volume_music', user_id)
            add_music(
                f'omni_{video_path}',
                'video',
                f'music/{music}',
                music_volume
            )

        if check_size(f'video/omni_{video_path}'):
            link = upload_to_fileio(f'video/omni_{video_path}')
            await bot.send_message(chat_id=user_id, text=f'Видео скачено!\n{link}')
        else:
            video = FSInputFile(f'video/omni_{video_path}')
            await bot.send_video(chat_id=user_id, video=video)

        os.remove(f'video/omni_{video_path}')

    await state.clear()
    clear_directory('TmpVideo')
    clear_directory('video')

