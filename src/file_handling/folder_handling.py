from pathlib import Path

def create_folder(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)