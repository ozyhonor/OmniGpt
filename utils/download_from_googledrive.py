import os


import gdown
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import string



def create_and_upload_file(dir_path='edit_content', name='ready.mp4'):
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


def download_from_drive(url):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()


    # Get the file ID from the URL
    file_id = url.split('id=')[-1]

    drive = GoogleDrive(gauth)

    # Get the file metadata
    file = drive.CreateFile({'id': file_id})
    file.FetchMetadata(fetch_all=True)

    # Get the file name
    file_name = file['title']
    print(file_name)
    if file_name in os.listdir('edit_content'):
        return file_name
    gdown.download(url, 'edit_content/'+file_name, quiet=False)
    return file_name