import os
from utils.cfg_loader import write_file

if not os.path.exists(r'./config/Remake'):
    os.mkdir(r'./config/Remake')

if not os.path.exists(r'./config/Remake/config.yml'):
    _cfg = dict(
        command=r'(重开|remake)\s*(\d+)?\s*(\w+)?\s*$',
        remake_perday=1
    )
    write_file(_cfg,r'./config/Remake/config.yml')