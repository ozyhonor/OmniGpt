from spawnbot import bot
from aiogram import Router, F
from  db.database import db
from aiogram.types import Message
from states.states import WaitingStateDoVideo
from aiogram.fsm.context import FSMContext
from utils.video.download import download
from utils.video.split_video_audio import split_video_and_get_subtitles
from menu.keyboards import CustomKeyboard
import os
from aiogram.types.input_file import FSInputFile
import shutil
from utils.video.clear_directory import clear_directory
from utils.video.check_size import check_size
from utils.video.convert_to_short_resol import change_resolution_video
from utils.download_from_googledrive import create_and_upload_file
from utils.video.create_video import VideoEditor, combine_video_chunks
from utils.video.split_video import split_timestamps


video_editor_router = Router()


@video_editor_router.message(F.text == '🛠️ Создать видео')
async def create_video_handler(message: Message, state: FSMContext):
    db.connect()
    await state.clear()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается youtube ссылка или файл формата mp4.', reply_markup=markup)
    await state.set_state(WaitingStateDoVideo.do_video)
    db.disconnect()


@video_editor_router.message(WaitingStateDoVideo.do_video)
async def process_video_handler(message: Message, state: FSMContext):
    '''

    1) crop
    2) perevod

    :param message:
    :param state:
    :return:
    '''
    db.connect()

    await message.answer('Скачиваю видео...')
    title = download(message.text)

    link = None
    user_id = message.from_user.id
    settings = db.get_user_settings(user_id)
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_shadow_color()
    time_crop = db.get_timestamps(user_id)
    print(time_crop)
    smart = db.get_smart_sub(user_id)

    print(title)
    for timestamp in time_crop.split(' '):
        if time_crop != '0':
            splited_timestamps = split_timestamps(timestamp.split('-'), 'video/'+title)
        else:splited_timestamps = False
        split_video_and_get_subtitles(smart, splited_timestamps or 'video/'+title, 'TmpVideo', settings['max_words'])
        files = ([i for i in os.listdir('TmpVideo') if i.endswith('.mp4') and '_' in i])
        files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        ready_files = []
        for file in files:

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
            os.rename(moved_file, os.path.join(target_path, new_name.format(title=title)))
        else:
            combine_video_chunks(ready_files, title)
        db.connect()
        if db.get_resolution(user_id) != 'original':
            change_resolution_video(title=f'video/omni_{title}')
        if check_size(f'video/omni_{title}'):
            link = create_and_upload_file(dir_path='video', name=f'omni_{title}')
        else:
            video = FSInputFile(f'video/omni_{title}')
            await bot.send_video(chat_id=user_id, video=video)
        os.remove(f'video/omni_{title}')



    await state.clear()
    clear_directory('TmpVideo')
    clear_directory('video')
    await message.answer(f'Видео скачено!\n{link}')
    db.disconnect()

