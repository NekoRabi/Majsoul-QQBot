from mirai import MessageChain

# 消息缓冲池


class msgbufferpool(object):
    '''
    Structure 结构

    好友消息(dict):
        好友1 : list
        好友2 : list

    群组消息(dict):
        群组1 (dict):
            群友1 : list

    '''

    def __init__(self):
        self.group = {}
        self.friend = {}

    def cleanup(self):
        self.group = {}
        self.friend = {}

    def addfriendmsg(self, senderid, msg):
        if not senderid in self.friend:
            self.friend[senderid] = []
        self.friend[senderid].append(msg)

    def addgroupmsg(self, groupid, senderid, msg):
        if not groupid in self.group:
            self.group[groupid] = {}

        if not senderid in self.group[groupid]:
            self.group[groupid][senderid] = []
        self.group[groupid][senderid].append = msg
