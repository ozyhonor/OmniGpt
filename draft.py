from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

generator = lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white')
subs = SubtitlesClip('subtitles.srt', generator)
subtitles = SubtitlesClip(subs, generator)

video = VideoFileClip("input.mp4")
result = CompositeVideoClip([video, subtitles.set_pos(('center','bottom'))])

result.write_videofile("output.mp4")
