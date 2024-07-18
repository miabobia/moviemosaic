"""
Fetch Data from rss feed then transform data into MovieClass objects.
Maybe we split this up into a fetch_data.py and a transform_data.py?
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

    # put in shared cache object here
    # it will check if 'filename' already exists
    # if it does then just return no further action needed
    # else call function regularly

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

    def remove_non_alphanum(s: str):
        return re.sub(r'[^a-zA-Z0-9]', '', s)

    def title_to_image_path(title: str):
        # make sure we are only taking alphanumeric characters
        # file_name = f"{images_dir}/{username}_{uuid.uuid4()}.png"

        title = remove_non_alphanum(title)

        images_dir = os.environ['IMAGES_DIR']
        return images_dir + title.replace(' ', '-') + '.png'

    # items = filter(has_watched_date, items)
    # # sorting movies by date
    # items = sorted(filter(is_movie, items), key=lambda x: get_watched_date(x), reverse=True)
    # # getting movies watched this month
    # items = list(filter(watched_this_month, items))

    items = valid_movies(user, month)

    movie_titles = list(map(get_movie_title, items))
    movie_ratings = list(map(get_movie_rating, items))
    movie_directors = list(map(get_director, map(get_tmdb_id, items)))
    movie_poster_paths = list(map(title_to_image_path, movie_titles))

    # download posters
    asyncio.run(download_all(zip(movie_poster_paths, map(get_poster_url, items))))
    
    # bundling up movies as dataclass now

    return [MovieCell(*movie_data) for movie_data in zip(movie_titles, movie_directors, movie_ratings, movie_poster_paths)]

class MovieCellBuilder:
    _username: str
    _mode: int
    _scraper: Scraper
    _transformer: Transformer

    # order of operations is way off here. Program will crash if rss feed isn't valid and transformer created
    def __init__(self, username: str, mode: int, month=0) -> None:
        self._scraper = Scraper(username=username)
        self._transformer = Transformer(username=username, mode=mode, month=month, feed_content=self._scraper.get_rss_feed())

    def valid_username(self) -> tuple(bool, str):
        if not self._scraper.valid_rss_feed():
            return False, f"{self._username} has no rss feed (most likely no letterboxd account)"
        if not self._transformer.valid_movies():
            # change message based on self._mode ??
            return False, f"{self._username} has no valid movies according to the criteria"

        return True, f'{self._username} is valid'

    def build_cells(self) -> list[MovieCell]:
        pass

# going to make this into a class to avoid duplicate calls because front-end makes calls here to determine if user valid
# every instance of Scraper needs to be tied to a server-side session
class Scraper:
    '''
    Scrape data from rss feed and return content.
    Can also check for invalid rss feed. 
    '''
    _rss_feed: bytes
    _username: str

    
    def __init__(self, username: str) -> None:
        self._username = username
        if mode == 'MONTH':
            self._mode = 0
        elif mode == 'MOST_RECENT':
            self._mode = 1

    def load_rss_feed(self) -> None:
        url = f'https://letterboxd.com/{self._username}/rss/'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        self._rss_feed = r.content
    
    def valid_rss_feed(self) -> bool:
        if not self.rss_feed:
            self.load_rss_feed()
        return "<title>Letterboxd - Not Found</title>" in self._rss_feed.decode("utf-8")

    def get_rss_feed(self) -> bytes:
        return self._rss_feed

class Transformer:
    '''
    Takes data from rss feed and transforms into usable state for building MovieCell objects.
    '''
    _username: str
    _mode: int
    _month: int
    _movies: list[str]

    def __init__(self, username: str, mode: int, month: int, feed_content: bytes):
        self._username = username
        self._mode = mode
        self._month = month
        self._movies = self.load_valid_movies(self.load_items(feed_content))

    def get_items(self, feed_content: bytes) -> list[str]:
        soup = BeautifulSoup(feed_content, 'xml')
        return soup.find_all('item')

    def load_valid_movies(self):
        def is_movie(item) -> bool:
            return  str(item.find('link')).find(f'https://letterboxd.com/{self._username}/list/') == -1 

        def watched_this_month(item) -> bool:
            return get_watched_date(item) == self._month
        
        def has_watched_date(item) -> bool:
            watched_token = re.split(pattern='<|>', string=str(item.find("letterboxd:watchedDate")))
            return watched_token != ['None']
        
        def get_watched_date(item) -> datetime:
            date_split = re.split(pattern='<|>', string=str(item.find("letterboxd:watchedDate")))[2].split('-')
            date = datetime(year=int(date_split[0]), month=int(date_split[1]), day=int(date_split[2]))
            # print(f'getwatched date returning: {date.month}')
            return date.month

        # ensure item has watched date field
        items = list(filter(has_watched_date, self.get_items()))

        # sorting movies by date
        items = sorted(filter(is_movie, items), key=lambda x: get_watched_date(x), reverse=True)

        if self._mode == 0:
            # getting movies watched this month
            items = list(filter(watched_this_month, items))
        elif self._mode == 1:
            # getting last 30 movies (change 30 to config.json val?)
            items = list(items)[:30]

        return items

    def valid_movies_exist(self) -> bool:
        return len(self._movies)