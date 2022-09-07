"""
:Author:  NekoRabi
:Create:  2022/9/6 21:00
:Update: /
:Describe: 缓冲池类
:Version: 0.0.2
"""

import time


class MessageBufferPool:
    """

    暂时弃用

    Structure 结构

    好友消息(dict):
        好友1 : list
        好友2 : list

    群组消息(dict):
        群组1 (dict):
            群友1 : list

    """

    def __init__(self):
        self.group = {}
        self.friend = {}

    def cleanup(self):
        self.group = {}
        self.friend = {}

    def addfriendmsg(self, senderid, msg):
        if senderid not in self.friend:
            self.friend[senderid] = []
        self.friend[senderid].append(msg)

    def addgroupmsg(self, groupid, senderid, msg):
        if groupid not in self.group:
            self.group[groupid] = {}

        if senderid not in self.group[groupid]:
            self.group[groupid][senderid] = []
        self.group[groupid][senderid].append = msg


class BotCommand:
    """指令父类"""

    type: str = 'BotCommand'

    def __init__(self):
        self.id = None
        self.command = None
        self.last_time = None

    def getcommand(self):
        return self.command

    def getlast_time(self):
        return self.last_time

    def getid(self):
        return self.id


class GroupCommand(BotCommand):
    """
    群指令类
    """
    type: str = 'GroupCommand'

    def __init__(self, groupid, userid, command: str, cd=10):
        """
        构造一条群指令，需要群号
        """
        super().__init__()
        self.groupid = groupid
        self.userid = userid
        self.command = command
        self.last_time = int(time.time())
        self.id = f'{groupid}_{userid}'
        self.duration = cd

    def __str__(self):
        return f'id:{self.id} ' \
               f'groupid:{self.groupid} ' \
               f'userid:{self.userid} ' \
               f'command:{self.command} ' \
               f'last_time:{self.last_time} '

    def __eq__(self, other):
        if isinstance(other, GroupCommand):
            if other.groupid == self.groupid and other.userid == self.userid and other.command == self.command:
                if -self.duration < other.last_time - self.last_time < self.duration:
                    return True
        return False

    def getgroupid(self):
        return self.groupid

    def getuserid(self):
        return self.userid


class LongTimeGroupCommand(GroupCommand):
    """
    长时间群指令类
    """
    type: str = 'LongTimeGroupCommand'

    def __init__(self, groupid, userid, command: str, cd=300):
        """
        构造一条长时间群指令，需要群号
        """
        super().__init__(groupid, userid, command, cd=300)

    def __str__(self):
        return f'id:{self.id} ' \
               f'groupid:{self.groupid} ' \
               f'userid:{self.userid} ' \
               f'command:{self.command} ' \
               f'last_time:{self.last_time} '

    def __eq__(self, other):
        if isinstance(other, GroupCommand):
            if other.groupid == self.groupid and other.userid == self.userid and other.command == self.command:
                if -self.duration < other.last_time - self.last_time < self.duration:
                    return True
        return False

    def getgroupid(self):
        return self.groupid

    def getuserid(self):
        return self.userid


class BotCommandCache:
    """
    群指令缓存区类
    """

    def __init__(self):
        self.groupbuffer = dict()

    def showallcmdincache(self) -> list:
        commandlist = []
        for k, v in self.groupbuffer.items():
            commandlist.append(v)
        return commandlist

    def getallcache(self):
        return self.groupbuffer

    def updategroupcache(self, command: BotCommand) -> bool:
        """
        更新指令缓存，更新成功/添加成功返回 True， 更新失败(10s内使用过)返回 False

        :param command: 命令
        :return: 更新成功/添加成功返回 True， 更新失败(10s内使用过)返回 False
        """
        if command.getid() in self.groupbuffer.keys():
            if command == self.groupbuffer[command.id]:
                # print("same cmd exist")
                return False
            else:
                self.groupbuffer[command.id] = command
                # print('update cmd cache')
                return True
        else:
            self.groupbuffer[command.id] = command
            # print('insert cmd')
            return True

    def pushcmd(self, command: GroupCommand):
        self.groupbuffer[command.id] = command

    def clearcache(self):
        self.groupbuffer = dict()

    def __str__(self):
        cmdstr = 'exist cmd :\n'
        for cmd in self.groupbuffer.values():
            cmdstr += f'{cmd}\n'
        return cmdstr


# TODO 做一个私聊指令缓冲池，并合并

cmdbuffer = BotCommandCache()
