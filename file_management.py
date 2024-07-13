import os
from glob import glob
import uuid
from PIL import Image

def file_cleanup():
    files = glob('images/*.png')
    for f in files:
        os.remove(f)

def file_saver(username: str, image: "Image") -> str:
    file_name = f"{username}_{uuid.uuid4()}.png"
    image.save(f"images/{file_name}")
    return file_name

def get_file_data(path: str) -> Image:
    return Image.open(path)