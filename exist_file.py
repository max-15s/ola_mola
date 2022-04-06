import pathlib
import checksumdir
from checksumdir import dirhash
import hashlib
import requests
from logzero import logger
import aiohttp
import aiofiles
import asyncio


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

    async def fetch(self, session: aiohttp.ClientSession, url: str, home, file) -> bool:
        """

        :param file:
        :param home:
        :param session:
        :param url:
        :return:
        """
        params = {
            'file_path': str(file)
        }
        save_path = self.storage / pathlib.Path(file).relative_to(home)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        for i in range(5):
            r = await session.post(url, params=params, ssl=False)
            if r.status == 200:
                async with aiofiles.open(save_path, 'wb') as f:
                    async for data in r.content.iter_any():
                        await f.write(data)
                if _get_directory_checksum(save_path) == r.headers['checksum']:
                    return True
        else:
            return False

    async def download_file(self, server, file_list, home2: pathlib.Path, root2: pathlib.Path) -> list:
        file_server = server + '/file'

        async with aiohttp.ClientSession() as session:
            var = await asyncio.gather(*[self.fetch(session, file_server, home2, file) for file in file_list])
            assert len(var) == sum(var), FileNotFoundError("files checksum don't match")

        folder_checksum = _get_directory_checksum(self.storage / root2)
        return [self.storage / root2, folder_checksum]

    def download_folder(self, taken_home: pathlib.Path, taken_root: pathlib.Path) -> bool:
        folder = self.get_response(taken_home, taken_root)
        for each in folder:
            loop = asyncio.get_event_loop()
            checksum = loop.run_until_complete(
                self.download_file(each['endpoint'], each['content'], taken_home, taken_root)
            )
            loop.close()
            response_checksum = requests.post(each['endpoint'] + '/checksum',
                                              params={'folder_root': str(taken_home) + str(taken_root)})
            md5 = response_checksum.json()
            if checksum[1] == md5['md5']:
                return True, each['endpoint']
            else:
                return False, each['endpoint']


async def main(url, file_list, home):
    d = downloaderClass('t5fr', 'edde')
    async with aiohttp.ClientSession() as session:
        var = await asyncio.gather(*[d.fetch(session, url, home, file) for file in file_list])
    print(var)


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
