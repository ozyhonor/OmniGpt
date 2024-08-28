import srt
from utils.video.video_editor import trim_by_timecode
import asyncio
import srt
import aiofiles

async def get_subtitles_content(file_path):
    """Подсчитывает количество субтитров в SRT файле."""
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        srt_content = await file.read()

    subtitles = list(srt.parse(srt_content))
    return subtitles


async def split_video_into_chunks(video_path, subtitles_path):
    subtitles = await get_subtitles_content(subtitles_path)
    video_chunks = []
    for chunk in subtitles:
        start, end = chunk.start, chunk.end
        video_fragment = await trim_by_timecode(video_path, start, end)
        video_chunks.append(video_fragment)

    return video_chunks

for _ in asyncio.run(get_subtitles_content('ттц.srt')):
    print(_)