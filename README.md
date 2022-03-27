# Objectivbe
- Create `mover_config.py` from `mover_config.py.example`
- Check the mover api
    - Give your IP to me to be whitelisted
- Create a downloader class
    1. Use aioHTTP
    1. First query the file list.
        1. If you get 404 move to next end_point
    1. Download each file, compare md5 of the file with the `checksum` in the header
        1. Use straeming download to log the downloading speed (after each file is downloaded)
    1. keep folder structure
    1. Check the folder checksum at the end of download and query it with API response