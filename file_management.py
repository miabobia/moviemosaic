import os
from glob import glob
import uuid
from PIL import Image
import io
import base64

def file_cleanup(filter_str: str=''):

    def filter_images(file_name) -> bool:
        return not filter_str in file_name

    if filter_str:
        files = list(filter(filter_images, glob('images/*.png')))
    
    for f in files:
        os.remove(f)

def file_saver(username: str, image: "Image") -> str:
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    file_name = f"images_dir/{username}_{uuid.uuid4()}.png"
    image.save(f"{file_name}")
    return file_name

def serve_image(image: Image) -> Image:
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_string

def read_image(image_path: str) -> Image:
    return Image.open(image_path)