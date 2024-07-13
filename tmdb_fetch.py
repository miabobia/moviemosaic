"""
Get director name from tmdb api using the tmdbsimple api
"""

import tmdbsimple as tmdb
import tmdb_auth
import os
tmdb.API_KEY = tmdb_auth.api_key
tmdb.API_KEY = os.environ['TMDB_API_KEY']



def get_director(movie_id: int) -> str:
    movie = tmdb.Movies(movie_id)
    response = movie.credits()['crew']
    director = None
    for role in response:
        if role['job'] == 'Director':
            director = role['name']
    return director