import pathlib
import checksumdir as checksumdir
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
                files = response.json()
                if files['status'] == 200:
                    response_checksum = requests.post(address + '/checksum',
                                                      params={'folder_root': str(home_response + root_response)})
                    md5 = response_checksum.json()
                    if 'files' in files:
                        servers.append({'endpoint': address, 'content': files['files'], 'checksum': md5['md5']})
                else:
                    logger.debug(f'{address}: Error {files["status"]}')
            except Exception as e:
                logger.debug(f'{e.__class__.__name__}: {address}')
                # logger.exception(e)
                # logger.debug('timeout')
        return servers

    def download_file(self, server, file_list, home2: pathlib.Path, root2: pathlib.Path) -> list:
        for file in file_list:
            params = {
                'file_path': str(file)
            }
            file_server = server + '/file'
            homee = pathlib.Path(str(home2).strip())
            roott = pathlib.Path(str(root2).strip())
            file_home = homee.joinpath(roott)
            with requests.post(file_server, params=params, stream=True) as response2:
                local_filename = self.storage / roott / pathlib.Path(file).relative_to(file_home)
                local_filename.parent.mkdir(parents=True, exist_ok=True)
                with open(local_filename, 'wb') as f:
                    for chunk in response2.iter_content(chunk_size=1024):
                        f.write(chunk)
            folder_checksum = _get_directory_checksum(self.storage / roott)
        return [self.storage / roott, folder_checksum]

    def download_folder(self, taken_home: pathlib.Path, taken_root: pathlib.Path): # -> bool:
        folder = self.get_response(taken_home, taken_root)
        for each in folder:
            checksum = self.download_file(each['endpoint'], each['content'], taken_home, taken_root)
            if checksum[1] == each['checksum']:
                return True, each['endpoint']
            else:
                return False


if __name__ == '__main__':
    import mover_config

    with open('file_path.txt', 'r') as r:
        home, root = r.readlines()

    d = downloaderClass(mover_config.STORAGE, mover_config.END_POINTS)
    result = d.download_folder(home.strip(), root.strip())
    if result is None:
        print("Files don't exist in any server")
    else:
        print(f"{result[1]}: {result[0]}")
