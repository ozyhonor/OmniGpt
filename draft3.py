import os


import gdown
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import string



def create_and_upload_file(dir_path='video', name='ready.mp4'):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    try:
        drive = GoogleDrive(gauth)
        if any([i for i in os.listdir(dir_path) if i == name]):...
        else:return

        my_file = drive.CreateFile({'title': f'{name}'})
        my_file.SetContentFile(os.path.join(dir_path, name))
        my_file.Upload()
        # Get the file ID
        file_id = my_file['id']
        permission = {
            'type': 'anyone',
            'role': 'reader',
            'value': ''
        }
        my_file.InsertPermission(permission)
        # Create the direct link for viewing
        direct_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        return direct_link
    except Exception as e:
        print(e)

create_and_upload_file(name = 'omni_mike_tyson_is_right_behind_you.mp4.mp4')