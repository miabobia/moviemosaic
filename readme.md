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
- add user's full name instead of username on generated image option (checkbox)
- add caching for movie posters
    - use shared memory/multiproccessing to handle cacheing
    - i wrote cache.py as an LRU cache with deque and set. Need to make instance of it and share between server.py and a worker process for proper caching
- change right side of image so it resizes based on max text length
- change font?

- figure out how to have data persist on server. Setting in disco.json i tried crashed server, but maybe syntax err?
- clean up server.py it is functional but lots of old code in there needs to be pruned. change pages so they follow correct convention eg (/userrr/ -> /user/)
- implement cleanup on the database. might need to add datetime stamps on TASKS table and not just RESULTS table
    - working on this but running into issues using crons. tasks will hang forever when this happens
- figure out how to implement flashes to display errors
- add gifs for progress messages? make progress messages display on main page instead of redirecting to loading screen?