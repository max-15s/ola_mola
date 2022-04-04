import pathlib
import checksumdir
from checksumdir import dirhash
import hashlib
import requests
from logzero import logger


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
            try:
                response = requests.post(server, params=params)
                if response.status_code == 200:
                    files = response.json()
                    if 'files' in files:
                        servers.append({'endpoint': address, 'content': files['files']})
                else:
                    logger.info(f'{address}: Error {response.status_code}')
            except Exception as e:
                logger.error(f'{e.__class__.__name__}: {address}')
                logger.exception(e)
        return servers

    def download_file(self, server, file_list, home2: pathlib.Path, root2: pathlib.Path) -> list:
        homee = pathlib.Path(str(home2).strip())
        roott = pathlib.Path(str(root2).strip())
        file_server = server + '/file'
        file_home = homee.joinpath(roott)
        for file in file_list:
            params = {
                'file_path': str(file)
            }
            with requests.post(file_server, params=params, stream=True) as response2:
                for i in range(5):
                    local_filename = self.storage / roott / pathlib.Path(file).relative_to(file_home)
                    local_filename.parent.mkdir(parents=True, exist_ok=True)
                    with open(local_filename, 'wb') as f:
                        for chunk in response2.iter_content(chunk_size=1024):
                            f.write(chunk)
                    file_checksum = _get_directory_checksum(local_filename)
                    if file_checksum == response2.headers['checksum']:
                        break
                    elif i >= 5:
                        raise FileNotFoundError("files checksum don't match")
        folder_checksum = _get_directory_checksum(self.storage / roott)
        return [self.storage / roott, folder_checksum]

    def download_folder(self, taken_home: pathlib.Path, taken_root: pathlib.Path):  # -> bool:
        folder = self.get_response(taken_home, taken_root)
        for each in folder:
            checksum = self.download_file(each['endpoint'], each['content'], taken_home, taken_root)
            response_checksum = requests.post(each['endpoint'] + '/checksum',
                                              params={'folder_root': str(taken_home) + str(taken_root)})
            md5 = response_checksum.json()
            if checksum[1] == md5['md5']:
                return True, each['endpoint']
            else:
                return False, each['endpoint']


if __name__ == '__main__':
    import mover_config

    with open('file_path.txt', 'r') as r:
        home, root = r.readlines()

    d = downloaderClass(mover_config.STORAGE, mover_config.END_POINTS)
    result = d.download_folder(home.strip(), root.strip())
    if result is None:
        print("No file exists!")
    else:
        print(f"{result[1]}: {result[0]}")
