"""
Get director name from tmdb api using the tmdbsimple api
"""

import tmdbsimple as tmdb
import os
tmdb.API_KEY = os.environ['TMDB_API_KEY']
movie: tmdb.Movies

def get_director(movie_id: int) -> str:
    '''
    Takes in tmdb movie id and returns director's name string
    '''
    movie = tmdb.Movies(movie_id)
    try:
        response = movie.credits()['crew']
        director = None
        for role in response:
            if role['job'] == 'Director':
                director = role['name']
    except:
        director = ''
    return director

def get_tmdb_poster_url(movie_id: int) -> str:
    '''
    Takes in tmdb movie id and returns url for poster
    '''

    #http://image.tmdb.org/t/p/w500/your_poster_path

    print(movie_id)

    movie = tmdb.Movies(movie_id)
    file_path = movie.images(include_image_language='en')['posters'][0]['file_path']

    # for key in image_dict:
    #     print(f'{key}')

    # file_path = image_dict['file_path']
    return f'http://image.tmdb.org/t/p/w500/{file_path}'