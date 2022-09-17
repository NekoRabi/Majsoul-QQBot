from utils.cfg_loader import *
import os

if not os.path.exists("./config/AutoReply"):
    os.mkdir("./config/AutoReply")

if not os.path.exists(r'./config/AutoReply/config.yml'):
    _cfg = dict(norepeat=False, norepeatgroup=[0], useAt=False, repeatconfig=dict(
        repeatQ=20, repeatmsg=1, interruptQ=0.5, interruptQQ=0.1, autoreply=True, kwreply=True))
    write_file(content=_cfg, path=r'./config/AutoReply/config.yml')
