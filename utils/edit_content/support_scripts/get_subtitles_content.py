import srt
import aiofiles

async def get_subtitles_content(file_path):
    """Подсчитывает количество субтитров в SRT файле."""
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        srt_content = await file.read()

    subtitles = list(srt.parse(srt_content))
    return subtitles