import os
from glob import glob
import uuid
def file_cleanup():
    files = glob('images/*.png')
    for f in files:
        os.remove(f)

def file_saver(username: str, image: "Image") -> str:
    file_name = f"{username}_{uuid.uuid4()}.png"
    image.save(f"images/{file_name}")
    return file_name