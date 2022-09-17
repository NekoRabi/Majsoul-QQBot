import os
from utils.cfg_loader import write_file


def file_init():
    if not os.path.exists("./config/TencentCloudAPI"):
        os.mkdir("./config/TencentCloudAPI")

    if not os.path.exists(r'./config/TencentCloudAPI/config.yml'):
        _cfg = {
            'secretId': '',
            'secretKey': '',
            'voicesetting': {
                'enable': False,
                'volume': 1,
                'speed': 0.9,
                'voicetype': 1002,
                'private': True,
                'codec': 'mp3'}
        }
        write_file(content=_cfg, path=r'./config/TencentCloudAPI/config.yml')


file_init()
