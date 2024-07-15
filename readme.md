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
- add stars onto posters
- add user's full name instead of username on generated image option (checkbox)
- add string sanitization
- add periodic file cleaning (current solution could have memory issues)
    - set expiry time on user generated images
    - linked list
        - when node added it has datetime
        - node expires based on current time - datetime == time threshold
        - only check head for expiry. 
        - when head expires we switch head -> head.next
- add caching for movie posters
    - set size of posters allowed to be stored locally
    - use deque to store image paths allowing us to quickly appendleft and pop
    - use set to store image paths allowing quick lookups to avoid duplicates
- more options for what movies can be retrieved?
    - last 30 movies (current issue is how i don't know how many movies are stored in rss feed)
    - I want to avoid headless browser solutions as they are slow for the hardware im using
    - re-request letterboxd api?

- improve efficiency of error checking. Currently duplicate calls are being made to rss feed to determine if provided username is valid
    - make scraping class so we can store rss feed when first check happens