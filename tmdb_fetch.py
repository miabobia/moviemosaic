"""
Get director name from tmdb api using the tmdbsimple api
"""

import tmdbsimple as tmdb
import os
tmdb.API_KEY = os.environ['TMDB_API_KEY']
movie: tmdb.Movies

def get_director(tmdb_id: int, tmdb_type: str) -> str:
    '''
    Takes in tmdb movie id and returns director's name string
    '''
    response: dict

    # print(f'TMDB_ID: {tmdb_id} TMDB_TYPE: {tmdb_type}')

    if tmdb_type == 'mv':
        movie = tmdb.Movies(tmdb_id)
        response = movie.credits()
    elif tmdb_type == 'tv':
        tv = tmdb.TV(tmdb_id)
        response = tv.credits()
        
    if not response or 'crew' not in response:
        return ''

    for role in response['crew']:
        if role['job'] == 'Director':
            return role['name']
    
    return ''

    # try:
    #     response = movie.credits()['crew']
    #     director = None
    #     for role in response:
    #         if role['job'] == 'Director':
    #             director = role['name']
    # except:
    #     director = ''
    # return director

def get_tmdb_poster_url(tmdb_id: int, tmdb_type: str) -> str:
    '''
    Takes in tmdb (movie or tv) id and returns url for poster
    '''
    # print(f'TMDB_ID: {tmdb_id} TMDB_TYPE: {tmdb_type}')
    #http://image.tmdb.org/t/p/w500/your_poster_path
    file_path: str = ''
    if tmdb_type == 'mv':
        movie = tmdb.Movies(tmdb_id)
        posters = movie.images(include_image_language='en')['posters']
        if not posters:
            posters = movie.images()['posters']
        if not posters:
            return None
        file_path = posters[0]['file_path']
    elif tmdb_type == 'tv':
        tv = tmdb.TV(tmdb_id)
        posters = tv.images(include_images='en')['posters']
        if not posters:
            posters = tv.images()['posters']
        if not posters:
            return None
        file_path = posters[0]['file_path']
            # return 'https://api.themoviedb.org/3/tv/{series_id}/images'
    
    # for key in image_dict:
    #     print(f'{key}')

    # file_path = image_dict['file_path']
    # print(f'file_path: {file_path}')
    return f'http://image.tmdb.org/t/p/w500/{file_path}'
