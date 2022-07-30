import time

from mirai import MessageChain


# 消息缓冲池


class msgbufferpool(object):
    """
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


class command:

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


class groupcommand(command):
    """
    群指令类
    """

    def __init__(self, groupid, userid, command: str):
        """
        构造一条群指令，需要群号
        """
        super().__init__()
        self.groupid = groupid
        self.userid = userid
        self.command = command
        self.last_time = int(time.time())
        self.id = f'{groupid}_{userid}'

    def __str__(self):
        return f'id:{self.id} groupid:{self.groupid} userid:{self.userid} command:{self.command} last_time:{self.last_time}'

    def __eq__(self, other):
        if type(other) == groupcommand:
            if other.groupid == self.groupid and other.userid == self.userid and other.command == self.command:
                if -10 < other.last_time - self.last_time < 10:
                    return True
        return False

    def getgroupid(self):
        return self.groupid

    def getuserid(self):
        return self.userid


class commandcache:
    """
        指令缓存区类
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

    def updategroupcache(self, command: command) -> bool:
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

    def pushcmd(self, command: groupcommand):
        self.groupbuffer[command.id] = command

    def clearcache(self):
        self.groupbuffer = dict()

    def __str__(self):
        cmdstr = 'exist cmd :\n'
        for cmd in self.groupbuffer.values():
            cmdstr += f'{cmd}\n'
        return cmdstr
