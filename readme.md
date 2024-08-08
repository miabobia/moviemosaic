# LETTERBOXD-GRID

Generates grid of movies recently watched by a letterboxd user and their ratings

## TODO
- css styling
    - banner
        - homebutton (image) -> need logo for this
    footer
        - socials links
    - need a brief description of how software works (eg: only pulls from diary, uses letterboxd)
- add user's full name instead of username on generated image option (checkbox)
- add caching for movie posters
    - use shared memory/multiproccessing to handle cacheing
    - i wrote cache.py as an LRU cache with deque and set. Need to make instance of it and share between server.py and a worker process for proper caching
- change font?
- there is something fishy going on with the username_info text. I think i set it up wrong for displaying the last date only if they choose the last 30 days option

- need to add options to display last month?

- add column to RESULTS table that stores file_paths. I want file_paths to images served up in dynamic page instead of inserting blobs straight into HTML so browser can cache
- database_janitor needs to account for this as well.