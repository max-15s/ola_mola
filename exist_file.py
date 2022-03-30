import pathlib
import checksumdir as checksumdir
from checksumdir import dirhash
import hashlib
import requests


def _get_directory_checksum(folder: pathlib.Path) -> str:
    if folder.is_dir():
        return dirhash(str(folder), 'md5')
    else:
        return checksumdir._filehash(str(folder), hashlib.md5)


class downloaderClass:
    def __init__(self, storage: pathlib.Path, endpoints: list):
        self.storage = storage
        self.endpoints = endpoints

    def get_response(self, home_response, root_response):
        servers = list()
        params = {
            'home': str(home_response),
            'root': str(root_response)
        }
        for address in self.endpoints:

            server = address + '/description'
            response = requests.post(server, params=params)
            files = response.json()
            # file_servers = address
            if 'files' in files:
                # for i in files['files']:
                #     self.download_file(pathlib.PurePosixPath(i.strip()), pathlib.PurePosixPath(home.strip()),
                #                          pathlib.PurePosixPath(root.strip()), file_servers)
                servers.append({'endpoint': address, 'content': response.json()})
        return servers

    def download_folder(self, home: pathlib.Path, root: pathlib.Path) -> bool:
        folder = self.get_response(home, root)[0]
        if self.download_file.response2.headers['checksum'] == _get_directory_checksum(pathlib.Path(self.download_file.local_filename)):
            return True
        else:
            return False


if __name__ == '__main__':
    import mover_config

    with open('file_path.txt', 'r') as r:
        home, root = r.readlines()

    d = downloaderClass(mover_config.STORAGE, mover_config.END_POINTS)
    print(d.download_folder(home, root))
