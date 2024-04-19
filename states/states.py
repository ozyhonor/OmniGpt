from aiogram.fsm.state import State, StatesGroup

stop_gpt = False
stop_eden = False

class WaitingPremium(StatesGroup):
    new_premium_id = State()

class WaitingYoutube(StatesGroup):
    video = State()
    playlist = State()


class WaitingStartSpeech(StatesGroup):
    rate = State()
    voice = State()
    text_speech = State()
    file_speech = State()
    queue_speech = State()


class WaitingStateDoVideo(StatesGroup):
    do_video = State()

class WaitingStateVideoSettings(StatesGroup):
    resolution = State()
    subtitles = State()
    translator = State()
    timestamps = State()
    format = State()
    size = State()
    source_language = State()
    translated_language = State()
    color = State()
    position = State()
    original_speed = State()
    translation_speed = State()
    outline = State()
    outline_size = State()
    outline_color = State()
    shadow = State()
    shadow_size = State()
    shadow_color = State()
    font = State()
    quality = State()
    max_words = State()
    id_settings_panel = State()


class WaitingStateGpt(StatesGroup):
    queue_files = State()
    settings = State()
    text_gpt = State()
    file_gpt = State()
    degree = State()
    theme = State()
