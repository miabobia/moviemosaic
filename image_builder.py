"""
Functions for building movie grid image.
To build call build(list[MovieCell], username: str)
"""

from PIL import Image, ImageDraw, ImageFont
from grid_shape import get_grid_size
import json
from functools import partial
import datetime
from math import ceil
import os


ICONS_DIR = os.environ['ICONS_DIR']
STAR_W, STAR_H = 12, 12 # make this into config.json val

def trans_paste(fg_img, bg_img, alpha=1.0, box=(0, 0)):
    fg_img_trans = Image.new("RGBA", fg_img.size)
    fg_img_trans = Image.blend(fg_img_trans,fg_img, alpha)
    bg_img.paste(fg_img_trans,box,fg_img_trans)
    return bg_img

def resize_image(im: Image, thumbnail_size: tuple) -> Image:
	return im.resize(size=thumbnail_size)

def build_thumbnail(cell: "MovieCell", thumbnail_size: tuple) -> Image:
	if not cell.im_path:
		return Image.open(os.environ['STATIC_DIR'] + '/NoPoster.png')
	return Image.open(cell.im_path)

def build_background(thumbnail_width: int, thumbnail_height: int,
					 grid_width: int, grid_height: int, text_width: int,
					 username_box_height: int, image_gap: int) -> Image:
	return Image.new(
		mode='RGBA', 
		size=(thumbnail_width * grid_width + image_gap * (grid_width + 1) + text_width,
			thumbnail_height * grid_height + image_gap * (grid_height + 1) + username_box_height),
		color=(50, 50, 50))

def get_max_text_size(text_drawer: ImageDraw, font: ImageFont, text_list: list) -> int:
	MIN_WIDTH = 300
	max_width = -1
	for text in text_list:
		max_width = max(text_drawer.textsize(text, font))
	return max(max_width, MIN_WIDTH)

def build_rating_image(movie_cell: "Moviecell", full_star: Image, half_star: Image, empty_star: Image) -> Image:

    # every star is 10x10*5 = (50x10)
    # create transparent image to paste stars onto
    backdrop = Image.new(
          mode='RGBA',
          size=(STAR_W*5, STAR_H),
          color=(255, 0, 0, 0)
    )
    order = ['e' for _ in range(5)]
    if movie_cell.rating != -1:
        half_stars = ceil(movie_cell.rating % 1)
        for i in range(int(movie_cell.rating)):
            order[i] = 'f'
        if half_stars:
            order[int(movie_cell.rating)] = 'h'
    
    # order list should be built now
    for index, code in enumerate(order):
        box = (index*STAR_W, 0, (index+1)*STAR_W, STAR_H)
        im: Image
        match code:
            case 'f':
                im = full_star
                pass
            case 'h':
                im = half_star
                pass
            case 'e':
                im = empty_star
                pass

        backdrop.paste(im=im, box=box)

    return backdrop


def build_movie_text(movie_cell: "MovieCell") -> str:
    mv_text = f' - {movie_cell.title} - {movie_cell.director}'
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
			config['image_gap'], 
			config['info_box_width'],
			config['username_box_height'],
			config['movie_info_font_size'],
			config['username_font_size'],
			config['font_color'],
			config['thumbnail_size']
			)


def build(movie_cells: list["MovieCell"], username: str, config_path: str, last_watch_date: datetime.datetime) -> Image.Image:
    '''
    Takes in list of MovieCell's and generates MovieMosaic image
    '''
    # loading config file
    image_gap, info_box_width, \
	username_box_height, movie_info_font_size, \
	username_font_size, font_color, thumbnail_size \
	= load_config(config_path)


    # create dynamically sized grid
    grid_width, grid_height = get_grid_size(len(movie_cells))

    # creating thumbnails
    thumbnails = list(map(partial(build_thumbnail, thumbnail_size=tuple(thumbnail_size)), movie_cells))
    thumb_width, thumb_height = thumbnails[0].size

    star_icons = [Image.open(ICONS_DIR + '/' + fp) for fp in ['full_rz.png', 'half_rz.png', 'empty_rz.png']]
    
    build_rating_image(movie_cells[0], *star_icons)

    
    # defining fonts
    info_font = ImageFont.truetype('./font/JuliaMono-Bold.ttf', movie_info_font_size, encoding='utf-8')
    username_font = ImageFont.truetype('./font/JuliaMono-Bold.ttf', username_font_size, encoding='utf-8')

    # load all movie_texts into a list then find max width
    movie_text = [build_movie_text(movie_cells[i]) for i in range(len(movie_cells))]
    # get_text_dimensions(username_str, info_font)
    max_movie_text = max(movie_text, key=lambda x: get_text_dimensions(x, info_font)[0])
    # print(max_movie_text)
    info_box_width = max(info_box_width, get_text_dimensions(max_movie_text, info_font)[0] + image_gap)

    # create background
    bg = build_background(thumb_width, thumb_height, grid_width, grid_height,
						  info_box_width, username_box_height, image_gap)
    text_drawer = ImageDraw.Draw(bg)

    # writing username and date to image
    my_date = datetime.datetime.now()
    username_str = f'{username} - '
    if last_watch_date:
        username_str = f'{username_str}{last_watch_date.strftime("%B")} {last_watch_date.strftime("%Y")} - {my_date.strftime("%B")} {my_date.strftime("%Y")}'		
    else:
        username_str = f'{username_str}{my_date.strftime("%B")} {my_date.strftime("%Y")}'
    
    username_width, username_height = get_text_dimensions(username_str, username_font)
    username_x = bg._size[0]//2 - username_width//2
    username_y = username_box_height//2 - username_height//2

    text_drawer.text((username_x, username_y), username_str, font=username_font,fill=tuple(font_color))

    cell_index = 0
	
    # paste thumbnails, text, and stars to background
    for j in range(grid_height):
        for i in range(grid_width):
            if cell_index >= len(movie_cells): break

            # thumbnails
            im_x = i * thumb_width + image_gap * (i+1)
            im_y = j * thumb_height + image_gap * (j+1) + username_box_height

            bg.paste(thumbnails[cell_index], (im_x, im_y))

            # text
            txt_x = grid_width * thumb_width + image_gap * (grid_width+1)
            txt_y = (j % grid_width) * thumb_height + image_gap * ((j % grid_width) + 1) + (i*20) + username_box_height

            txt_str = movie_text[cell_index]

            text_drawer.text((txt_x + (STAR_W*5), txt_y), txt_str, font=info_font, fill=tuple(font_color))

            # bg.paste(build_rating_image(movie_cells[cell_index], *star_icons), (txt_x, txt_y + 5))

            # bg.paste(star, (im_x, im_y + star.size[1] - star.size[1]))

            # bg = trans_paste(star, bg, alpha=1.0, box=(im_x, im_y + star.size[1] - star.size[1]))
            bg = trans_paste(build_rating_image(movie_cells[cell_index], *star_icons), bg, alpha=1.0, box=(txt_x, txt_y+(STAR_H//2) - 1))
            cell_index += 1

    return bg
