from pathlib import Path

def create_folder(directory):
    print('creating folder: ', directory)
    Path(directory).mkdir(parents=True, exist_ok=True)