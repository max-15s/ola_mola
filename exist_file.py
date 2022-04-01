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
            # file_servers = address
            if 'files' in files:
                # for i in files['files']:
                #     self.download_file(pathlib.PurePosixPath(i.strip()), pathlib.PurePosixPath(home.strip()),
                #                          pathlib.PurePosixPath(root.strip()), file_servers)
                servers.append({'endpoint': address, 'content': files['files']})
        return servers

    def download_file(self, server, file_list) -> list:
        for file in file_list:
            file_address = server
            params = {
                'file_path': str(file_address)
            }
            file_server = server + '/file'
            file2 = file_address
            file_home = str(home.joinpath(root))
            with requests.post(file_server, params=params, stream=True) as response2:
                local_filename = self.storage / root / file2.relative_to(file_home)
                local_filename.parent.mkdir(parents=True, exist_ok=True)
                with open(local_filename, 'wb') as f:
                    for chunk in response2.iter_content(chunk_size=1024):
                        f.write(chunk)
        folder_checksum = _get_directory_checksum(pathlib.Path(local_filename))
        return [local_filename, folder_checksum]

    def download_folder(self, home: pathlib.Path, root: pathlib.Path) -> bool:
        folder = self.get_response(home, root)
        for each in folder:
            self.download_file(each['endpoint'], each['content'])
        if folder:
            return True
        # if self.download_file.response2.headers['checksum'] == \
        #         _get_directory_checksum(pathlib.Path(self.download_file.local_filename)):
        #     return True
        # else:
        #     return False


if __name__ == '__main__':
    import mover_config

    with open('file_path.txt', 'r') as r:
        home, root = r.readlines()

    d = downloaderClass(mover_config.STORAGE, mover_config.END_POINTS)
    print(d.download_folder(home.strip(), root.strip()))
