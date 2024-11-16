from aiogram.fsm.state import State, StatesGroup

stop_gpt = False
stop_eden = False

class WaitingPremium(StatesGroup):
    new_premium_id = State()

class WaitingYoutube(StatesGroup):
    video = State()
    playlist = State()
    link = State()


class WaitingStateTranslator(StatesGroup):
    text_translate = State()
    file_translate = State()


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
    sample = State()
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
    music = State()
    shadow_color = State()
    font = State()
    quality = State()
    max_words = State()
    id_settings_panel = State(),
    volume_music = State()

class WaitingStateVision(StatesGroup):
    vision_photo = State()
    vision_file = State()
    vision_settings = State()
    vision_model = State()

class WaitingStateGpt(StatesGroup):
    postsettings = State()
    postmodel = State()
    queue_files = State()
    settings = State()
    text_gpt = State()
    file_gpt = State()
    model = State()
    degree = State()
    theme = State()
    tokens = State()
