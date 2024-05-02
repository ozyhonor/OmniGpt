from utils.checkUrl import check_url
from utils.download_from_googledrive import download_from_drive
from utils.video.download_video import download_video
from db.database import db
from utils.download_subtitles import download_video_subtitles


def download(url, user_id):
    if check_url(url) == 'Google Drive File':
        return download_from_drive(url)
    elif check_url(url) == 'YouTube':
        if db.get_user_settings('interesting_moment', user_id):
            download_video_subtitles(url, user_id)
        return download_video(url)
