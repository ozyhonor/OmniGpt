import os


def check_size(file):

    file_size_bytes = os.path.getsize(file)
    file_size_mb = file_size_bytes / (1024 * 1024)
    if file_size_mb > 25:
        return True
    else:
        return False