"""
eventually API calls will be in place here to extract data
"""

from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
from tmdb_fetch import get_director
import aiohttp
import asyncio
import aiofiles
from moviecell import MovieCell
import os

async def download(name_url: tuple[str], session):
    url = name_url[1]
    filename = name_url[0]
    async with session.get(url) as response:
        async with aiofiles.open(filename, "wb") as f:
            await f.write(await response.read())

async def download_all(name_urls: list[tuple]):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[download(name_url, session=session) for name_url in name_urls]
        )

def rss_feed_exists(username: str) -> bool:
    # inefficient extra call to url here need to fix!
    url = f'https://letterboxd.com/{username}/rss/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, headers=headers)
    
    return not "<title>Letterboxd - Not Found</title>" in r.content.decode("utf-8")

def valid_movies(username: str, month: int):

    url = f'https://letterboxd.com/{username}/rss/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, headers=headers)

    # shouldn't need this anymore since it is called before scrape externally
    # if rss_feed_exists(r.content):
    #     raise Exception("ERROR: Username does not exist")
    


    soup = BeautifulSoup(r.content, 'xml')

    items = soup.find_all('item')

    def is_movie(item) -> bool:
        return  str(item.find('link')).find(f'https://letterboxd.com/{username}/list/') == -1 

    def watched_this_month(item) -> bool:
        return get_watched_date(item) == month
    
    def has_watched_date(item) -> bool:
        watched_token = re.split(pattern='<|>', string=str(item.find("letterboxd:watchedDate")))
        return watched_token != ['None']
    
    def get_watched_date(item) -> datetime:
        date_split = re.split(pattern='<|>', string=str(item.find("letterboxd:watchedDate")))[2].split('-')
        date = datetime(year=int(date_split[0]), month=int(date_split[1]), day=int(date_split[2]))
        # print(f'getwatched date returning: {date.month}')
        return date.month
    
    items = list(filter(has_watched_date, items))

    # print(f'ITEM AFTER HAS WATCH DATE:\n\n{items}\n\n')
    # sorting movies by date
    items = sorted(filter(is_movie, items), key=lambda x: get_watched_date(x), reverse=True)

    # getting movies watched this month
    items = list(filter(watched_this_month, items))

    return items

def scrape(user: str, month: int) -> list:
    # maybe we split this up into two funcs

    # url = f'https://letterboxd.com/{user}/rss/'
    # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    # r = requests.get(url, headers=headers)

    # # shouldn't need this anymore since it is called before scrape externally
    # # if rss_feed_exists(r.content):
    # #     raise Exception("ERROR: Username does not exist")
    


    # soup = BeautifulSoup(r.content, 'xml')

    # items = soup.find_all('item')

    def is_movie(item) -> bool:
        return  str(item.find('link')).find(f'https://letterboxd.com/{user}/list/') == -1 

    def watched_this_month(item) -> bool:
        return get_watched_date(item).month == month
    
    def has_watched_date(item) -> bool:
        watched_token = item.find("letterboxd:watchedDate")
        return watched_token != None

    def get_watched_date(item) -> datetime:
        # print(item,end='\n\n')
        splitter = re.split(pattern='<|>', string=str(item.find("letterboxd:watchedDate")))
        # print(splitter,end='\n\n')
        date_split = re.split(pattern='<|>', string=str(item.find("letterboxd:watchedDate")))[2].split('-')
        date = datetime(year=int(date_split[0]), month=int(date_split[1]), day=int(date_split[2]))
        return date
    
    def get_movie_title(item) -> str:
        return re.split(pattern='<|>', string=str(item.find("letterboxd:filmTitle")))[2]

    def get_movie_rating(item) -> int:
        rating_tag = item.find("letterboxd:memberRating")
        if not rating_tag: return -1
        return float(re.split(pattern='<|>', string=str(rating_tag))[2])

    def get_poster_url(item) -> str:
        # attrs are broken inside description tag so we have to do this a little more manually
        url_slice = [m.start() for m in re.finditer('"', str(item.find('description')))]
        return str(item.find('description'))[url_slice[0]+1:url_slice[1]]

    def get_tmdb_id(item) -> int:
        return int(re.split(pattern='<|>', string=str(item.find("tmdb:movieId")))[2])

    def title_to_image_path(path: str):
        images_dir = os.path.join(os.path.dirname(__file__), 'images/')
        return images_dir + path.replace(' ', '-') + '.png'

    # items = filter(has_watched_date, items)
    # # sorting movies by date
    # items = sorted(filter(is_movie, items), key=lambda x: get_watched_date(x), reverse=True)
    # # getting movies watched this month
    # items = list(filter(watched_this_month, items))

    items = valid_movies(user, month)

    # reverse these? ^^    
    movie_titles = list(map(get_movie_title, items))
    movie_ratings = list(map(get_movie_rating, items))
    movie_directors = list(map(get_director, map(get_tmdb_id, items)))
    movie_poster_paths = list(map(title_to_image_path, movie_titles))

    # download posters
    asyncio.run(download_all(zip(movie_poster_paths, map(get_poster_url, items))))
    
    # bundling up movies as dataclass now

    return [MovieCell(*movie_data) for movie_data in zip(movie_titles, movie_directors, movie_ratings, movie_poster_paths)]