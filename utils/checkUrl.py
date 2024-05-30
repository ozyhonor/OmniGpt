import requests
import re

def check_url(url):
    google_drive_pattern = r"^(http(s)?:\/\/)?((w){3}.)?drive.google.com\/file\/d\/.+"

    youtube_pattern = r"^(http(s)?:\/\/)?((w){3}.)?youtu((be)|(be.com))?(\/|.*)"

    if re.match(youtube_pattern, url):
        return "YouTube"
    elif re.match(google_drive_pattern, url):
        return "Google Drive File"
    else:
        return "Unknown"