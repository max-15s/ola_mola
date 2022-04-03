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

    def get_response(self, home_response, root_response) -> list:
        servers = list()
        params = {
            'home': str(home_response),
            'root': str(root_response)
        }
        for address in self.endpoints:
            server = address + '/description'
            response = requests.post(server, params=params)
            files = response.json()
            response_checksum = requests.post(address + '/checksum', params={'folder_root': str(home_response + root_response)})
            md5 = response_checksum.json()
            if 'files' in files:
                servers.append({'endpoint': address, 'content': files['files'], 'checksum': md5['md5']})
        return servers

    def download_file(self, server, file_list, home2, root2) -> list:
        for file in file_list:
            params = {
                'file_path': str(server)
            }
            file_server = server + '/file'
            homee = pathlib.Path(home2.strip())
            roott = pathlib.Path(root2.strip())
            file_home = homee.joinpath(roott)
            with requests.post(file_server, params=params, stream=True) as response2:
                local_filename = self.storage / roott / pathlib.Path(file).relative_to(file_home)
                local_filename.parent.mkdir(parents=True, exist_ok=True)
                with open(local_filename, 'wb') as f:
                    for chunk in response2.iter_content(chunk_size=1024):
                        f.write(chunk)
            folder_checksum = _get_directory_checksum(self.storage / roott)
        return [self.storage / roott, folder_checksum]

    def download_folder(self, taken_home: pathlib.Path, taken_root: pathlib.Path) -> bool:
        folder = self.get_response(taken_home, taken_root)
        for each in folder:
            checksum = self.download_file(each['endpoint'], each['content'], taken_home, taken_root)
            if checksum[1] == each['checksum']:
                return True
            else:
                return False


if __name__ == '__main__':
    import mover_config

    with open('file_path.txt', 'r') as r:
        home, root = r.readlines()

    d = downloaderClass(mover_config.STORAGE, mover_config.END_POINTS)
    print(d.download_folder(home.strip(), root.strip()))
