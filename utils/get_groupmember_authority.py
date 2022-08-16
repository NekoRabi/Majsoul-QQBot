from mirai import GroupMessage
from core import config


def get_group_msgsender_authority(event: GroupMessage):
    return event.sender.permission


def is_havingadmin(event: GroupMessage):
    if event.sender.id in config.get('admin', []):
        return True
    elif event.sender.permission == "MEMBER":
        return False
    return True
