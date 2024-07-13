"""
Functions for building movie grid image.
To build call build(list[MovieCell], username: str)
"""

from PIL import Image, ImageDraw, ImageFont
from grid_shape import get_grid_size
import json
from functools import partial
import datetime

def trans_paste(fg_img, bg_img, alpha=1.0, box=(0, 0)):
    fg_img_trans = Image.new("RGBA", fg_img.size)
    fg_img_trans = Image.blend(fg_img_trans,fg_img, alpha)
    bg_img.paste(fg_img_trans,box,fg_img_trans)
    return bg_img

def resize_image(im: Image, w_factor: float, h_factor: float) -> Image:
	new_size = (int(im.size[0] * w_factor), int(im.size[1] * h_factor))
	return im.resize(size=new_size)

def build_thumbnail(cell: "MovieCell", resize_factor: float) -> Image:
	return resize_image(Image.open(cell.im_path), resize_factor, resize_factor)

def build_background(thumbnail_width: int, thumbnail_height: int,
					 grid_width: int, grid_height: int, text_width: int,
					 username_box_height: int, image_gap: int) -> Image:
	return Image.new(
		mode='RGBA', 
		size=(thumbnail_width * grid_width + image_gap * (grid_width + 1) + text_width,
			thumbnail_height * grid_height + image_gap * (grid_height + 1) + username_box_height),
		color=(50, 50, 50))

def get_max_text_size(text_drawer: ImageDraw, font: ImageFont, text_list: list) -> int:
	WIDTH_LIMIT = 500
	max_width = -1
	for text in text_list:
		max_width = max(text_drawer.textsize(text, font))
	return min(max_width, WIDTH_LIMIT)

def build_movie_text(movie_cell: "MovieCell") -> str:
	mv_text = f'{movie_cell.title} - {movie_cell.director}'
	if len(mv_text) > 68:
		director = movie_cell.director.split(' ')
		director[-1] = director[-1][0]
		mv_text = f'{movie_cell.title} - {' '.join(map(str, director)) }'
	return mv_text

def get_text_dimensions(text_string: str, font: ImageFont.truetype):
    # https://stackoverflow.com/a/46220683/9263761
    _, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def load_config(path: str) -> list:
	config: dict
	with open(path, 'r') as f:
		config = json.load(f)
	return (
		    config['resize_factor'],
			config['image_gap'], 
			config['info_box_width'],
			config['username_box_height'],
			config['movie_info_font_size'],
			config['username_font_size'],
			config['font_color']
			)


def build(movie_cells: list["MovieCell"], username: str, config_path: str) -> Image.Image:

    # loading config file
    resize_factor, image_gap, info_box_width, \
	username_box_height, movie_info_font_size, \
	username_font_size, font_color = load_config(config_path)

    # create dynamically sized grid
    grid_width, grid_height = get_grid_size(len(movie_cells))
	
    # creating thumbnails
    thumbnails = list(map(partial(build_thumbnail, resize_factor=resize_factor), movie_cells))
    thumb_width, thumb_height = thumbnails[0].size

    # create background
    bg = build_background(thumb_width, thumb_height, grid_width, grid_height,
						  info_box_width, username_box_height, image_gap)
    
    # defining fonts
    info_font = ImageFont.truetype('./font/JuliaMono-Bold.ttf', movie_info_font_size, encoding='utf-8')
    username_font = ImageFont.truetype('./font/JuliaMono-Bold.ttf', username_font_size, encoding='utf-8')
    text_drawer = ImageDraw.Draw(bg)
	
    # writing username and date to image
    my_date = datetime.datetime.now()
    username_str = f'{username} - {my_date.strftime("%B")} {my_date.strftime("%Y")}'
    username_width, username_height = get_text_dimensions(username_str, username_font)
    username_x = bg._size[0]//2 - username_width//2
    username_y = username_box_height//2 - username_height//2

    text_drawer.text((username_x, username_y), username_str, font=username_font,fill=tuple(font_color))

    cell_index = 0
	
    # paste thumbnails, text, and stars to background
    for i in range(grid_width):
        for j in range(grid_height):
            if cell_index >= len(movie_cells): break

            # thumbnails
            im_x = i * thumb_width + image_gap * (i+1)
            im_y = j * thumb_height + image_gap * (j+1) + username_box_height

            bg.paste(thumbnails[cell_index], (im_x, im_y))

            # text
            txt_x = grid_width * thumb_width + image_gap * (grid_width+1)
            txt_y = (j % grid_width) * thumb_height + image_gap * ((j % grid_width) + 1) + (i*20) + username_box_height

            txt_str = build_movie_text(movie_cells[cell_index])
            print(f'{txt_str} -> {len(txt_str)}')

            text_drawer.text((txt_x, txt_y), txt_str, font=info_font, fill=tuple(font_color))

            # bg.paste(star, (im_x, im_y + star.size[1] - star.size[1]))

            # bg = trans_paste(star, bg, alpha=1.0, box=(im_x, im_y + star.size[1] - star.size[1]))
            cell_index += 1

    return bg