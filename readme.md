# LETTERBOXD-GRID

Generates grid of movies recently watched by a letterboxd user and their ratings

"star.png" is Designed by Freepik user [@juicy_fish](https://www.freepik.com/author/juicy-fish)

## TODO
- css styling
    - banner
        - homebutton (image) -> need logo for this
    footer
        - socials links
    - need a brief description of how software works (eg: only pulls from diary, uses letterboxd)
- add stars onto posters (add ratings onto text field instead?)
- add user's full name instead of username on generated image option (checkbox)
- add caching for movie posters
    - use shared memory/multiproccessing to handle cacheing
    - i wrote cache.py as an LRU cache with deque and set. Need to make instance of it and share between server.py and a worker process for proper caching
- more options for what movies can be retrieved?
    - add option to fetch last 30 (50 is max) movies from rss
- change right side of image so it resizes based on max text length
- 

# BUGS
- any url is reachable without crashing ?
- is there any tmdb entries without posters/titles?
- movies are being displayed in incorrect order like this:
    0 3 6
    1 4 7
    2 5 8

want them in this order
    0 1 2
    3 4 5
    6 7 8
