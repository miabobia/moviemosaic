import os
from glob import glob
import uuid
from PIL import Image
import io
import base64

def file_cleanup(filter_list: list):

    def filter_images(file_name) -> bool:
        for check_str in filter_list:
            if check_str in file_name:
                return False
        return True

    images_dir = os.environ['IMAGES_DIR']
    # images_dir = os.path.join(os.path.dirname(__file__), 'images/')
    files = list(filter(filter_images, glob(f'{images_dir}*.png')))
    
    for f in files:
        os.remove(f)

def file_saver(username: str, image: "Image"='') -> str:
    # images_dir = os.path.join(os.path.dirname(__file__), 'images/')
    print('hello world')
    images_dir = os.environ['IMAGES_DIR']
    file_name = f"{images_dir}/{username}_{uuid.uuid4()}.png"
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