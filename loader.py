from handlers.start import start_router
from handlers.premium import premium_router
from handlers.gpt_handlers.gpt_router import gpt_router
from handlers.gpt_handlers.gpt_text import gpt_text
from handlers.gpt_handlers.gpt_file_queue import gpt_file_queue
from handlers.gpt_handlers.gpt_settings import gpt_settings
from handlers.gpt_handlers.gpt_file import gpt_file
from handlers.vision.vision_photo import vision_photo_router
from handlers.text_to_speech_gpt.speech_router import speech_router
from handlers.text_to_speech_gpt.speech_settings import speech_settings_router
from handlers.text_to_speech_gpt.speech_text import speech_text_router
from handlers.text_to_speech_gpt.speech_file import speech_file_router
from handlers.youtube_handlers.youtube_router import youtube_router
from handlers.youtube_handlers.youtube_video import youtube_video_router
from handlers.youtube_handlers.youtube_playlist import youtube_playlist_router
from handlers.videoeditor_handlers.video_router import video_router
from handlers.videoeditor_handlers.video_settings_router import video_settings_router
from handlers.videoeditor_handlers.video_editor_router import video_editor_router
from handlers.youtube_handlers.youtube_settings import youtube_settings_router
from handlers.vision.vision_router import vision_router
from handlers.translator_handlers.translator_router import translator_router
from handlers.vision.vision_settings import vision_settings_router
from handlers.picture_generation.picture_router import picture_router

import sys
import logging
import asyncio
from spawnbot import dp, bot


logging.basicConfig(level=logging.INFO,
                    handlers=[
                        logging.StreamHandler(sys.stdout)  # output to file AND console
                    ],
                    format="%(asctime)s - %(levelname)s\t%(module)s/%(funcName)s:%(lineno)d\t- %(message)s",
                    datefmt='%d/%m/%Y %H:%M:%S',
                    )


async def on_startup(_):
    logging.info('Bot started.')


async def main() -> None:
    dp.include_routers(
        premium_router,
        start_router,
        gpt_router,
        gpt_file,
        gpt_file_queue,
        gpt_text,
        gpt_settings,
        speech_router,
        speech_settings_router,
        speech_text_router,
        speech_file_router,
        youtube_router,
        youtube_video_router,
        youtube_playlist_router,
        video_router,
        video_settings_router,
        video_editor_router,
        youtube_settings_router,
        translator_router,
        vision_router,
        vision_photo_router,
        vision_settings_router,
        picture_router

    )
    await dp.start_polling(bot, on_startup=on_startup)

if __name__ == '__main__':
    asyncio.run(main())

