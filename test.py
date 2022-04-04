# files = self.get_response(address, pathlib.PurePosixPath(home.strip()), pathlib.PurePosixPath(root.strip()))


# def download_file(self, file_address: pathlib.Path, home: pathlib.Path, root: pathlib.Path, server) -> bool:
#     params = {
#         'file_path': str(file_address)
#     }
#     file_server = server + '/file'
#     file2 = file_address
#     file_home = str(home.joinpath(root))
#     with requests.post(file_server, params=params, stream=True) as response2:
#         local_filename = self.storage / root / file2.relative_to(file_home)
#         local_filename.parent.mkdir(parents=True, exist_ok=True)
#         with open(local_filename, 'wb') as f:
#             for chunk in response2.iter_content(chunk_size=1024):
#                 f.write(chunk)