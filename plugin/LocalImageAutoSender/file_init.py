import os

from core import add_help
from utils.cfg_loader import write_file, read_file

if not os.path.exists("./config/LocalImageAutoSender"):
    os.mkdir("./config/LocalImageAutoSender")


def _build_config():
    cfg = dict(dragonimg=True)
    write_file(content=cfg, path="./config/LocalImageAutoSender/config.yml")


_fun_key = ['dragonimg']


def _file_verification():
    if os.path.exists("./config/LocalImageAutoSender/config.yml"):
        cfg = read_file("./config/LocalImageAutoSender/config.yml")
        for key in _fun_key:
            if key not in cfg.keys():
                _build_config()
                break
    else:
        _build_config()


_file_verification()

add_help('group', ["龙图: 发龙图\n"])