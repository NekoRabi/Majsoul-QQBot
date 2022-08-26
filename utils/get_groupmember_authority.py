from mirai import GroupMessage
from utils.cfg_loader import loadcfg_from_file

_config = loadcfg_from_file(r'./config/config.yml')

__all__ = ['get_group_msgsender_authority', 'is_havingadmin']


def get_group_msgsender_authority(event: GroupMessage):
    return event.sender.permission


def is_havingadmin(event: GroupMessage):
    if event.sender.id in _config.get('admin', []):
        return True
    elif event.sender.permission == "MEMBER":
        return False
    return True
