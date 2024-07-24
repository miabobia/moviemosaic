"""
Get director name from tmdb api using the tmdbsimple api
"""

import tmdbsimple as tmdb
import os
tmdb.API_KEY = os.environ['TMDB_API_KEY']



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

def get_poster(movie_id: int) -> str:
    '''
    Takes in tmdb movie id and returns url for poster
    '''
    pass