from moviepy.editor import VideoFileClip

def get_video_resolution(video_path):
    video_clip = VideoFileClip(video_path)
    resolution = {'w': video_clip.size[0], 'h': video_clip.size[1]}
    video_clip.close()
    return resolution