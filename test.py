import pathlib
import mover_config
import checksumdir as checksumdir
from checksumdir import dirhash
import hashlib
import requests


def get_response():
    headers = {
        'accept': 'application/json',
    }

    params = {
        'home': '/opt/rahkar/udemy/json_panel/udemy/',
        'root': '2503776',
    }

    response = requests.post('http://64.20.61.237:1258/description/', headers=headers, params=params)
    print(response.json())
    return response.json()


get_response()
#
# d = get_response(mover_config.STORAGE, mover_config.END_POINTS)
#
# # d.download_folder(pathlib.Path(home.strip()), pathlib.Path(root.strip()))
# address = mover_config.END_POINTS[0] + '/description'
# d.get_response(address, pathlib.Path(home.strip()), pathlib.Path(root.strip()))