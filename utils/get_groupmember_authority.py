"""
:Author:  NekoRabi
:Create:  2022/9/18 2:58
:Update: /
:Describe: 获取群成员的权限
:Version: 0.0.2
"""
from mirai import GroupMessage
from utils.cfg_loader import read_file

_config = read_file(r'./config/config.yml')

__all__ = ['get_group_msgsender_authority', 'is_having_admin_permission']


def get_group_msgsender_authority(event: GroupMessage):
    """

    Args:
        event: 群消息事件

    Returns:群成员的权限  群主/管理员/普通成员

    """
    return event.sender.permission


def is_having_admin_permission(event: GroupMessage):
    """

    Args:
        event: 群消息事件

    Returns:  是否有机器人的管理权限

    """
    if event.sender.id in _config.get('admin', []):
        return True
    elif event.sender.permission == "MEMBER":
        return False
    return True
