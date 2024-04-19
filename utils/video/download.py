from utils.checkUrl import check_url
from utils.download_from_googledrive import download_from_drive
from utils.video.download_video import download_video


def download(url):
    if check_url(url) == 'Google Drive File': return download_from_drive(url)
    elif check_url(url) == 'YouTube': return download_video(url)
