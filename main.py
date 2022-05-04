import nest_asyncio
import re
import websockets.exceptions

from plugin import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai import FriendMessage, GroupMessage, Plain, Startup, Shutdown, At, MessageChain, \
    Image, MessageEvent
from mirai.models import MemberJoinEvent, NudgeEvent

if __name__ == '__main__':

    nest_asyncio.apply()
    create_folders()
    config = load_config()
    replydata = load_replydata()
    create_helpimg()

    rootLogger = create_logger(config['loglevel'])
    qqlogger = getQQlogger()

    black_list = dict(user=[], group=[])
    black_list['user'] = config['blacklist']
    black_list['group'] = config['mutegrouplist']
    whiteList = config['whitelist']
    admin: list = config['admin']
    master = config['master']
    settings = config['settings']
    botname = config['botconfig']['botname']
    commandpre = config['commandpre']
    alarmclockgroup = config['alarmclockgroup']
    silencegroup = config['silencegroup']
    repeatconfig = config['repeatconfig']
    norepeatgroup = config['norepeatgroup']
    qhsettings = config['qhsettings']
    disnudgegroup = config['disnudgegroup']

    bot = create_bot(config)

    if master not in admin:
        admin.append(master)
    print(f"机器人{botname}启动中\tQQ : {bot.qq}\nadapter : {bot.adapter_info}")

    replydata = ditc_shuffle(replydata)


    # 自动获取雀魂牌谱
    async def qh_autopaipu():
        result = autoQueryPaipu()
        logging.info(result)
        for info in result:
            for group in info['groups']:
                await bot.send_group_message(group, info['text'])
        return


    async def asyqh_autopaipu():
        result = asygetqhpaipu()
        print("查询新的雀魂对局信息有:")
        print(result)
        for msgobj in result:
            for group in msgobj['groups']:
                await bot.send_group_message(group, msgobj['msg'])
        return


    async def asyth_all():
        result = asygetTH()
        print("开始查询天凤信息")
        print(result)
        for msgobj in result:
            for group in msgobj['groups']:
                await bot.send_group_message(group, msgobj['msg'])
        return


    # 自动获取天凤对局 - 普通爬虫
    async def th_autopaipu():
        print("开始查询天风结算信息")
        msglist = autoget_th_match()
        print(f'正在进行的对局有{msglist}')
        for msgobj in msglist:
            for group in msgobj['groups']:
                await bot.send_group_message(group, msgobj['msg'])


    # 自动获取天凤对局 - 异步爬虫
    async def asyth_autopaipu():
        print("开始查询天风结算信息")
        tasks = [asyncio.ensure_future(asyautoget_th_match())]
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*tasks)
        loop.run_until_complete(tasks)
        for results in tasks.result():
            if len(results) > 0:
                print(f'正在进行的对局有{results}')
                for msgobj in results:
                    for group in msgobj['groups']:
                        await bot.send_group_message(group, msgobj['msg'])
        return


    # 自动广播天凤对局开始信息
    async def asyth_broadcastmatch():
        print("开始查询天风对局信息")

        tasks = [asyncio.ensure_future(asyautoget_th_matching())]
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*tasks)
        loop.run_until_complete(tasks)

        for results in tasks.result():
            if len(results) > 0:
                print(f'结算信息有:{results}')
                for msgobj in results:
                    for group in msgobj['groups']:
                        await bot.send_group_message(group, msgobj['msg'])
        return


    async def th_broadcastmatch():
        print("开始查询天风对局信息")
        msglist = autoget_th_matching()
        for msgobj in msglist:
            for group in msgobj['groups']:
                await bot.send_group_message(group, msgobj['msg'])
        return


    # 获取天凤的相关信息
    async def asyth_auto():
        print("开始查询天凤相关信息")
        tasks = [asyncio.ensure_future(asyautoget_th_matching()), asyncio.ensure_future(asyautoget_th_match())]
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*tasks)
        loop.run_until_complete(tasks)

        for results in tasks.result():
            if len(results) > 0:
                for msgobj in results:
                    for group in msgobj['groups']:
                        await bot.send_group_message(group, msgobj['msg'])
        return


    def get_groupsender_permission(event: GroupMessage):
        return event.sender.permission


    def is_havingadmin(event: GroupMessage):
        if event.sender.id in admin:
            return True
        elif event.sender.permission == "MEMBER":
            return False
        return True


    def getreply(reply: list = None, text: str = None, rndimg: bool = False, imgpath: str = None) -> MessageChain:
        msgchain = []
        if reply:
            msgchain.append(Plain(random.choice(reply)))
        if text:
            msgchain.append(Plain(text))
        if reply or text:
            msgchain.append(Plain(random.choice(replydata['suffix'])))
        if rndimg:
            msgchain.append(
                Image(path=f"./data/reply/img/{replydata['replyimgpath']}/{random.choice(replydata['img'])}"))
        if imgpath:
            msgchain.append(
                Image(path=f"{imgpath}"))
        return MessageChain(msgchain)


    # 聊天记录存储
    @bot.on(MessageEvent)
    def addEventLog(event: MessageEvent):
        if event.type == 'GroupMessage':
            # infodict = dict(type=event.type,senderid=event.sender.id,sendername=event.sender.get_name(),
            # groupname=event.group.name,groupid=event.group.id,message=event.message_chain)
            # qqlogger.info(infodict)
            qqlogger.info(event)
        else:
            qqlogger.info(event)


    # 欢迎

    @bot.on(MemberJoinEvent)
    async def welcome(event: MemberJoinEvent) -> None:
        if settings['autowelcome']:
            personid = event.member.id
            personname = event.member.member_name
            groupname = event.member.group.name
            info: str = random.choice(config['welcomeinfo'])
            info = info.replace('%ps%', personname)
            info = info.replace('%gn%', groupname)
            msg = MessageChain([
                At(personid),
                Plain(f" {info}")
            ])

            await bot.send_group_message(event.member.group.id, msg)
            await petpet(personid)
            await bot.send_group_message(event.member.group.id,
                                         MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{personid}.gif')))
            return


    @bot.on(FriendMessage)
    async def asyspidertest(event: FriendMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}freshqh\s*$", msg.strip())
            if m:
                print("牌谱刷新中")
                await bot.send(event, "牌谱刷新中")
                await asyqh_autopaipu()


    @bot.on(FriendMessage)
    async def addadmin(event: FriendMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}addadmin\s*(\d+)\s*$", msg.strip())
            if m:
                if not m.group(1) in admin:
                    admin.append(int(m.group(1)))

                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    return await bot.send(event, MessageChain(Plain(f" 已将 {m.group(1)} 添加为机器人管理员")))
                else:
                    return await bot.send(event, MessageChain(Plain(f" {m.group(1)}已经是管理员了")))
        return


    @bot.on(FriendMessage)
    async def deladmin(event: FriendMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}deladmin\s*(\d+)\s*$", msg.strip())
            if m:
                if m.group(1) in admin:
                    admin.remove(int(m.group(1)))
                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    return await bot.send(event, MessageChain(Plain(f" 已将 {m.group(1)} 从机器人管理员中移出")))
                else:
                    return await bot.send(event, MessageChain(Plain(f" {m.group(1)}不是管理员了")))
        return


    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')


    '''获取日志'''


    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}log\s*(\w+)?\s*(\d+)\s*$", msg.strip())
            if m:
                if m.group(1):
                    if m.group(2):
                        return
                    else:
                        return
                else:
                    return
            return


    # PING

    @bot.on(FriendMessage)
    async def ping(event: FriendMessage):
        if event.message_chain.has("ping"):
            rootLogger.info("ping了一下")
            await bot.send(event, "pong!")
        return


    # 强制复读

    @bot.on(FriendMessage)
    async def sendmsgTogroup(event: FriendMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}stext::\s*([0-9]+)\s*([\u4e00-\u9fa5\w%&',;=?!^.$\x22，。？！]+)\s*$", msg.strip())
            if m:
                return await bot.send_group_message(int(m.group(1)), m.group(2))


    @bot.on(GroupMessage)
    async def forceAt(event: GroupMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}at::\s*([\u4e00-\u9fa5\w%&',@;=?!^.$\x22，。？！]+)\s*$", msg.strip())
            if m:
                if At in event.message_chain:
                    target = event.message_chain.get_first(At).target
                    return await bot.send(event, MessageChain([At(target), Plain(f" {m.group(1)}")]))


    @bot.on(GroupMessage)
    async def enablesetu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(open|enable|开启)\s*(涩图|色图|setu)\s*$', msg.strip())
        if m:
            if is_havingadmin(event):
                groupid = event.group.id
                if groupid in config['setugroups']:
                    await bot.send(event, getreply(text="本群已开启色图", rndimg=True))
                else:
                    config['setugroups'].append(groupid)
                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    await bot.send(event, getreply(text="色图开启成功", rndimg=True))


    @bot.on(GroupMessage)
    async def disablesetu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(fr'^{commandpre}(close|disable|关闭)\s*(涩图|色图|setu)\s*$', msg.strip())
        if m:
            if is_havingadmin(event):
                groupid = event.group.id
                if groupid in config['setugroups']:
                    config['setugroups'].remove(groupid)
                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    await bot.send(event, getreply(text="色图已关闭", rndimg=True))
                else:
                    await bot.send(event, getreply(text="本群色图已关闭", rndimg=True))


    @bot.on(GroupMessage)
    async def setu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m1 = re.match(fr'^{commandpre}(色图|涩图|setu)\s*([\w\d]+)?\s*$', msg.strip())
        m2 = re.match(fr"^{commandpre}来(\d)*(张|份)([\w\d]+)?\s*(的)?\s*(色图|涩图)\s*$", msg.strip())
        if m1:
            if random.random() * 100 < 10:
                print(f"发出对{event.sender.id}的少冲提醒")
                await bot.send(event, [At(event.sender.id), " 能不能少冲点啊，这次就不给你发了"])
            else:
                if settings['setu'] and event.group.id in config['setugroups']:
                    imginfo = getsetu(m1.group(2))
                    if imginfo['notFound']:
                        await bot.send(event, getreply(text="没找到该图片呢"))
                        return
                    try:
                        await bot.send(event, MessageChain([Image(url=imginfo['url'])]))
                    except Exception as e:
                        print(f"色图请求失败:{e}")
                        await bot.send(event, MessageChain([Plain(f"出错了!这肯定不是{botname}的问题!")]))
        elif m2:
            if random.random() * 100 < 10:
                print(f"发出对{event.sender.id}的少冲提醒")
                await bot.send(event, [At(event.sender.id), " 能不能少冲点啊，这次就不给你发了"])
            else:
                if settings['setu'] and event.group.id in config['setugroups']:
                    imginfo = getsetu(m2.group(3),m2.group(2))
                    if imginfo['notFound']:
                        await bot.send(event, getreply(text="没找到该图片呢"))
                        return
                    try:
                        await bot.send(event, MessageChain([Image(url=imginfo['url'])]))
                    except Exception as e:
                        print(f"色图请求失败:{e}")
                        await bot.send(event, MessageChain([Plain(f"出错了!这肯定不是{botname}的问题!")]))
        return


    """雀魂相关"""


    @bot.on(MessageEvent)
    async def getmajsoulhelp(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(help|帮助)\s*$', msg.strip())
        if m:
            return await bot.send(event, Image(path="./images/help.png"))


    # 禁用功能

    @bot.on(GroupMessage)
    async def disableqhplugin(event: GroupMessage):
        # 匹配指令
        if is_havingadmin(event) or event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(fr'^{commandpre}disable\s*(\w+)\s*$', msg.strip())
            if m:
                command = m.group(1)
                group = event.group.id
                if command in ['qhpt', '雀魂分数', '雀魂pt']:
                    if group not in qhsettings['disptgroup']:
                        qhsettings['disptgroup'].append(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'查分功能禁用成功')
                elif command in ['qhpaipu', '雀魂最近对局']:
                    if group not in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].append(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')
                elif command in ['qhinfo', '雀魂玩家详情']:
                    if group not in qhsettings['disinfogroup']:
                        qhsettings['disinfogroup'].append(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'雀魂玩家详情功能禁用成功')
                elif command in ['qhsl', '雀魂十连']:
                    if group not in qhsettings['disybgroup']:
                        qhsettings['disybgroup'].append(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'模拟十连功能禁用成功')
                elif command in ['qhyb', '雀魂月报']:
                    if group not in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].append(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')


    @bot.on(GroupMessage)
    async def enableqhplugin(event: GroupMessage):
        # 匹配指令
        if is_havingadmin(event) or event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(fr'^{commandpre}enable\s*(\w+)\s*$', msg.strip())
            if m:
                command = m.group(1)
                group = event.group.id
                if command in ['qhpt', '雀魂分数', '雀魂pt']:
                    if group in qhsettings['disptgroup']:
                        qhsettings['disptgroup'].remove(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'查分功能启用成功')
                elif command in ['qhpaipu', '雀魂最近对局']:
                    if group in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].remove(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')
                elif command in ['qhinfo', '雀魂玩家详情']:
                    if group in qhsettings['disinfogroup']:
                        qhsettings['disinfogroup'].remove(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'雀魂玩家详情功能禁用成功')
                elif command in ['qhsl', '雀魂十连']:
                    if group in qhsettings['disybgroup']:
                        qhsettings['disybgroup'].remove(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'模拟十连功能禁用成功')
                elif command in ['qhyb', '雀魂月报']:
                    if group in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].remove(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')


    # 查分

    @bot.on(GroupMessage)
    async def qhpt(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhpt|雀魂分数|雀魂pt)\s*([\w_、,\.，\'\"!]+)\s*([34])?\s*([0-9]+)?\s*$', msg.strip())
        if m:
            if qhsettings['qhpt'] and event.group.id not in qhsettings['disptgroup']:
                if m.group(3):
                    if m.group(4):
                        await bot.send(event, getcertaininfo(m.group(2), m.group(3), int(m.group(4))))
                    else:
                        await bot.send(event, getcertaininfo(m.group(2), m.group(3)))
                else:
                    await bot.send(event, query(m.group(2)))
            return


    @bot.on(GroupMessage)
    async def getrecentqhpaipu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr'^{commandpre}(qhpaipu|雀魂最近对局)\s*([\w_、,\.，\'\"!]+)\s*([34])*\s*([0-9]+)?\s*$', msg.strip())
        if m:
            if qhsettings['qhpaipu'] and event.group.id not in qhsettings['dispaipugroup']:
                playername = m.group(2)
                searchtype = m.group(3)
                if searchtype:
                    if searchtype not in ['3', '4']:
                        await bot.send(event, '牌局参数有误，请输入 3 或 4')
                        return
                    if m.group(4):
                        searchnumber = int(m.group(4))
                        if 0 < searchnumber < 11:
                            await bot.send(event,
                                           getsomeqhpaipu(playername=playername, type=searchtype, counts=searchnumber))
                            return
                        else:
                            await bot.send(event, "牌局数量有误，最多支持10场牌局")
                            return
                    else:
                        await bot.send(event, getsomeqhpaipu(playername=playername, type=searchtype))


    @bot.on(GroupMessage)
    async def getplayerdetails(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(
            fr'^{commandpre}(qhinfo|雀魂玩家详情)\s*([\w_、,\.，\'\"!]+)\s*(\d+)\s*(\w+)*\s*(\w+)*\s*$', msg.strip())
        if m:
            if qhsettings['qhinfo'] and event.group.id not in qhsettings['disinfogroup']:

                playername = m.group(2)
                selecttype = m.group(3)
                model = m.group(4)
                selectlevel = m.group(5)
                if selectlevel:
                    pass
                else:
                    if model is None:
                        model = '基本'
                    detail = getplayerdetail(playername=playername, selecttype=selecttype, model=model)
                    if detail['error']:
                        await bot.send(event, detail['msg'])
                    else:
                        await bot.send(event, Image(path=f'./images/MajsoulInfo/detail{playername}.png'))
        return


    @bot.on(GroupMessage)
    async def getmondetails(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(
            fr'^{commandpre}(qhyb|雀魂月报)\s*([\w_、,\.，\'\"!]+)\s*(3|4)\s*([0-9]{{1,4}})\-([0-9]{{1,2}})\s*$', msg.strip())
        if m:
            if qhsettings['qhyb'] and event.group.id not in qhsettings['disybgroup']:
                playername = m.group(2)
                selecttype = m.group(3)
                year = m.group(4)
                month = m.group(5)
                report = getmonthreport(playername=playername, selecttype=selecttype, year=year, month=month)
                if report['error']:
                    await bot.send(event, report['msg'])
                else:
                    await bot.send(event, MessageChain([Image(path=f'./images/MajsoulInfo/yb{playername}.png')]))
        return


    # 获取某群的雀魂关注人员

    @bot.on(GroupMessage)
    async def getqhwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhgetwatch|雀魂获取本群关注)\s*$', msg.strip())
        if m:
            await bot.send(event, getallwatcher(event.group.id))


    # 将一个雀魂用户加入某群的关注

    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhadd|雀魂添加关注)\s*([\w_、,\.，\'\"!]+)\s*$', msg.strip())
        if m:
            if event.group.id not in qhsettings['disautoquerygroup']:
                # if is_havingadmin(event):
                #     await bot.send(event, addwatch(m.group(2), event.group.id))
                # else:
                #     await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))
                await bot.send(event, addwatch(m.group(2), event.group.id))


    # 删除某群雀魂关注

    @bot.on(GroupMessage)
    async def delwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhdel|雀魂删除关注)\s*([\w_、,\.，\'\"!]+)\s*$', msg.strip())
        if m:
            if event.group.id not in qhsettings['disautoquerygroup']:
                # if is_havingadmin(event):
                #     await bot.send(event,
                #                    removewatch(playername=m.group(2), groupid=event.group.id))
                # else:
                #     await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))
                await bot.send(event, removewatch(m.group(2), event.group.id))
        return


    # 来一发雀魂十连

    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(qhsl|雀魂十连)\s*(\w+)*\s*$', msg.strip())
        if m:
            if qhsettings['qhsl'] and event.group.id not in qhsettings['disslgroup']:
                if m.group(2):
                    if m.group(2) in ['限时', '限定', 'up', 'UP']:
                        result = drawcards(userid=event.sender.id, up=True)
                        if result['error']:
                            return await bot.send(event,
                                                  MessageChain([At(event.sender.id), Plain(result['resultsmsg'])]))
                        mergeimgs(result.get('results'), event.sender.id)
                        await bot.send(event, MessageChain([
                            At(event.sender.id),
                            Plain("\n 抽卡结果:\n"),
                            Image(path=f"./images/MajSoulInfo/{event.sender.id}.png")]))
                        # return await bot.send(event, MessageChain([
                        #     At(event.sender.id),
                        #     Plain(result['resultsmsg'])
                        # ]))
                    elif m.group(2) in ['常驻', '普通', 'common', 'normal']:
                        result = drawcards(userid=event.sender.id, up=False)
                        if result['error']:
                            return await bot.send(event,
                                                  MessageChain([At(event.sender.id), Plain(result['resultsmsg'])]))
                        mergeimgs(result.get('results'), event.sender.id)
                        await bot.send(event, MessageChain([
                            At(event.sender.id),
                            Plain("\n 抽卡结果:\n"),
                            Image(path=f"./images/MajSoulInfo/{event.sender.id}.png")]))
                        # return await bot.send(event, MessageChain([
                        #     At(event.sender.id),
                        #     Plain(result['resultsmsg'])
                        # ]))
                    else:
                        result = drawcards(userid=event.sender.id, up=False)
                        if result['error']:
                            return await bot.send(event,
                                                  MessageChain([At(event.sender.id), Plain(result['resultsmsg'])]))
                        await bot.send(event,
                                       MessageChain([At(event.sender.id), Plain('参数输入有误，请输入“限时”或“常驻”，此次十连将输出常驻')]))
                        mergeimgs(
                            result.get('results'), event.sender.id)
                        await bot.send(event, MessageChain([
                            At(event.sender.id),
                            Plain("\n 抽卡结果:\n"),
                            Image(path=f"./images/MajSoulInfo/{event.sender.id}.png")]))
                        # return await bot.send(event, MessageChain([
                        #     At(event.sender.id),
                        #     Plain(result['resultsmsg'])
                        # ]))
                else:
                    result = drawcards(userid=event.sender.id, up=False)
                    if result['error']:
                        return await bot.send(event, MessageChain([At(event.sender.id), Plain(result['resultsmsg'])]))
                    mergeimgs(
                        result.get('results'), event.sender.id)
                    await bot.send(event, MessageChain([
                        At(event.sender.id),
                        Plain("\n 抽卡结果:\n"),
                        Image(path=f"./images/MajSoulInfo/{event.sender.id}.png")]))
            else:
                return await bot.send(event, getreply(text="此群已禁用模拟抽卡"))
        return


    '''天凤相关'''


    @bot.on(GroupMessage)
    async def addtenhouwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(thpt|天凤pt|天凤分数)\s*([\w_、,，\'\\\.!]+)\s*$', msg.strip())
        if m:
            await bot.send(event, getthpt(m.group(2)))


    @bot.on(GroupMessage)
    async def addtenhouwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(thadd|天凤添加关注)\s*([\w_、,，\'\\\.!]+)\s*$', msg.strip())
        if m:
            if is_havingadmin(event):
                await bot.send(event, addthwatch(m.group(2), event.group.id))
            else:
                await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))


    @bot.on(GroupMessage)
    async def deltenhouwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(thdel|天凤删除关注)\s*([\w_、,，\'\\\.!]+)\s*$', msg.strip())
        if m:
            if is_havingadmin(event):
                await bot.send(event,
                               removethwatch(playername=m.group(2), groupid=event.group.id))
            else:
                await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))


    @bot.on(GroupMessage)
    async def gettenhouwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(thgetwatch|天凤获取本群关注)\s*$', msg.strip())
        if m:
            await bot.send(event, getthwatch(event.group.id))


    '''通用功能'''

    '''随机搞怪回复'''


    @bot.on(GroupMessage)
    async def duideduide(event: GroupMessage):
        if not settings['silence']:
            if event.group.id not in silencegroup:
                if len(event.message_chain[Plain]) == 1:
                    msg = str(event.message_chain[Plain][0]).strip()
                    # if msg in ['正确的', '错误的', '辩证的', '对的对的', '啊对对对',"理性的","中肯的",'客观的','整体的','全面的']:
                    #     if random.random() * 100 < 30:
                    #         await bot.send(event, random.choice(['正确的', '错误的', '辩证的', '对的对的', '不对的', '对的对的']))

                    if msg in ['正确的', '直接的', '中肯的', '雅致的', '客观的', '整体的', '立体的', '全面的', '辩证的', '形而上学的', '雅俗共赏的', '一针见血的',
                               '直击要害的', '错误的', '间接的', '虚伪的', '庸俗的', '主观的', '平面的', '片面的', '孤立的', '辩证法的', '雅俗之分',
                               '的离题万里的',
                               '不痛不痒的']:
                        if random.random() * 100 < 30:
                            await bot.send(event, random.choice(
                                ['正确的', '直接的', '中肯的', '雅致的', '客观的', '整体的', '立体的', '全面的', '辩证的', '形而上学的', '雅俗共赏的',
                                 '一针见血的',
                                 '直击要害的', '错误的', '间接的', '虚伪的', '庸俗的', '主观的', '平面的', '片面的', '孤立的', '辩证法的', '雅俗之分的',
                                 '离题万里的',
                                 '不痛不痒的']))
                    # 方舟肉鸽词库
                    elif msg in ['迷茫的', '盲目的', '孤独的', '生存的', '臆想的', '谨慎的', '暴怒的', '偏执的', '敏感的']:
                        if random.random() * 100 < 30:
                            await bot.send(event, random.choice(
                                ['正确的', '错误的', '辩证的', '迷茫的', '盲目的', '孤独的', '生存的', '臆想的', '谨慎的', '暴怒的', '偏执的', '敏感的']))


    '''创建举牌文字'''


    @bot.on(MessageEvent)
    async def jupai(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr'''^{commandpre}举牌\s*([\u4e00-\u9fa5\w_%&',;:=?!^.$\x22，。？！]+)\s*$''', msg.strip())
        if m:
            if len(m.group(1)) > 40:
                await bot.send(event, "最多支持做40个字的举牌哦~")
            imgoutput(event.sender.id, (m.group(1)))
            message_chain = MessageChain([
                await Image.from_local(f'./images/jupai/{event.sender.id}.png')
            ])
            await bot.send(event, message_chain)


    '''获取机器人信息'''


    @bot.on(FriendMessage)
    async def getbotinfo(event: FriendMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        m = re.match(fr'^{commandpre}getinfo\s*$', msg.strip())
        if m:
            if userid in admin:
                return await bot.send(event,
                                      f"机器人设置:{config}\n白名单用户:{whiteList}\n黑名单用户:{black_list['user']}\n屏蔽群组:{black_list['group']}")


    '''沉默机器人'''


    # 全局沉默
    @bot.on(FriendMessage)
    async def besilence(event: FriendMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            userid = event.sender.id
            # 匹配指令
            m = re.match(fr'^{commandpre}silence\s*(\w+)\s*$', msg.strip())
            if m:
                if m.group(1).lower() == 'on' or m.group(1).lower() == 'true':
                    settings['silence'] = True
                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                else:
                    settings['silence'] = False
                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)


    # 单群沉默 - 从群聊沉默
    @bot.on(GroupMessage)
    async def begroupsilencebygroup(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        if userid in admin:
            m = re.match(fr'^{commandpre}silence\s*(\w+)\s*$', msg.strip())
            if m:
                if m.group(1).lower() == 'on' or m.group(1).lower() == 'true':
                    if event.group.id not in silencegroup:
                        silencegroup.append(event.group.id)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                else:
                    if event.group.id in silencegroup:
                        silencegroup.remove(event.group.id)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)


    # 关闭复读
    @bot.on(GroupMessage)
    async def norepeatbygroup(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        if userid in admin:
            m = re.match(fr'^{commandpre}norepeat\s*(\w+)\s*$', msg.strip())
            if m:
                if m.group(1).lower() == 'on' or m.group(1).lower() == 'true':
                    print(f'已将{event.group.id}的复读关闭')
                    if event.group.id not in norepeatgroup:
                        norepeatgroup.append(event.group.id)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                else:
                    if event.group.id in norepeatgroup:
                        print(f'已将{event.group.id}的复读开启')
                        norepeatgroup.remove(event.group.id)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)


    # 添加白名单

    @bot.on(GroupMessage)
    async def addwhitelist(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        m = re.match(fr'^{commandpre}addwhitelist\s*([0-9]+)\s*$', msg.strip())
        if m:
            if userid in admin and userid not in whiteList:

                whiteList.append(int(m.group(1)))
                with open(r'./config.yml', 'w') as file:
                    yaml.dump(config, file, allow_unicode=True)
                print(m)
                return await bot.send(event, "添加成功")
            else:
                return await bot.send(event, "添加失败,用户已存在")


    # 添加黑名单

    @bot.on(FriendMessage)
    async def addblacklist(event: FriendMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        m = re.match(fr'^{commandpre}addblacklist\s*([0-9]+)\s*$', msg.strip())
        if m:
            if userid in admin:
                if int(m.group(1)) in admin:
                    return await bot.send(event, "请不要将管理员加入黑名单")
                black_list['user'].append(int(m.group(1)))
                print(black_list['user'])
                with open(r'./config.yml', 'w') as file:
                    yaml.dump(config, file, allow_unicode=True)
                print(m)
                return await bot.send(event, "添加成功")
            else:
                return await bot.send(event, "添加失败,用户已存在")


    # 移出黑名单

    @bot.on(FriendMessage)
    async def delblacklist(event: FriendMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        m = re.match(fr'^{commandpre}delblacklist\s*([0-9]+)\s*$', msg.strip())
        if m:
            if userid in admin:
                delperson = int(m.group(1))
                if delperson in black_list['user']:
                    black_list['user'].remove(delperson)
                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    return await bot.send(event, "删除成功")
                else:
                    return await bot.send(event, "删除失败,用户不存在")


    '''随机打断、复读、嘲讽'''


    @bot.on(GroupMessage)
    async def on_group_message(event: GroupMessage):
        if not (settings['silence'] or settings['norepeat']):
            if event.group.id not in silencegroup:
                if event.group.id not in norepeatgroup:
                    count = random.random() * 100
                    msg = event.message_chain[Plain]
                    senderid = event.sender.id
                    if senderid in whiteList:
                        return
                    if str(event.message_chain) in ['?', "？"] and count < repeatconfig['repeatQ']:
                        print(f"在{event.group.name}群,复读了一次?")
                        return await bot.send(event, "?")
                    if count < repeatconfig['interruptQQ']:
                        print(f"在{event.group.name}群,打断一次{msg}")
                        return await bot.send(event, random.choice(["¿", "?????"]))
                    elif count < repeatconfig['interruptQ']:
                        print(f"在{event.group.name}群,打断一次{msg}")
                        return await bot.send(event, "?")
                    elif count < repeatconfig['repeatmsg']:
                        print(f"在{event.group.name}群,复读一次{msg}")
                        return await bot.send(event, event.message_chain)
        return


    # 获取项目地址

    @bot.on(MessageEvent)
    async def getlink(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}项目地址\s*$", msg.strip())
        if m:
            return await bot.send(event, MessageChain([Plain(
                "Github : https://github.com/NekoRabi/Majsoul-QQBot\nGitee : "
                "https://gitee.com/Syaro/Majsoul-QQBot\n如果觉得好可以点个star⭐")]))

            # 与机器人互动


    last_bvid = {}


    @bot.on(GroupMessage)
    # 哔哩哔哩解析
    async def bili_resolve(event: GroupMessage):
        if not settings['silence']:
            if event.group.id not in silencegroup:
                global last_bvid
                text = str(event.message_chain.as_mirai_code)
                text = text.replace('\\n', '').replace('\\', '')
                if 'b23.tv/' in text:
                    b23_url = re.findall('b23.tv/[A-Za-z0-9]+', text)[0]
                    url = f'https://{b23_url}'
                    resp = requests.get(url, allow_redirects=False)
                    text = resp.text
                if 'BV' in text:
                    bvid = re.findall('BV[A-Za-z0-9]+', text)[0]
                else:
                    return
                if event.group.id in last_bvid.keys():
                    if bvid == last_bvid[event.group.id]:
                        return
                # if event.message_chain.has("www.bilibili.com/video"):
                #     bvid = re.findall('BV[A-Za-z0-9]',"".join(map(str, event.message_chain[Plain])).strip())[0]
                last_bvid[event.group.id] = bvid
                bv_url = f'http://api.bilibili.com/x/web-interface/view?bvid={bvid}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=bv_url) as resp:
                        data = await resp.json()
                if data['code'] != 0:
                    return
                img_url = data['data']['pic']
                author = data['data']['owner']['name']
                title = data['data']['title']
                msg = f'{bvid}\nUP主:{author}\n标题:{title}'
                '''if event.message_chain[1].type == 'App':
                    app = event.message_chain[1].as_json()
                    url = app['meta']['detail_1']['preview']
                    img_url = f'http://{url}'''
                message_chain = MessageChain([Image(url=img_url), Plain(text=msg)])
                return await bot.send(event, message_chain)


    @bot.on(GroupMessage)
    async def diyreply(event: GroupMessage):
        if not settings['silence']:
            if event.group.id not in silencegroup:
                msg = "".join(map(str, event.message_chain[Plain]))
                m = re.match(fr'^{commandpre}([\w\d]+)鸡打\s*\.', msg.strip())
                if m:
                    if '呆' not in m.group(1):
                        return await bot.send(event,
                                              f"{m.group(1)}说，他有五个鸡，我说，立直鸡，副露鸡，默听鸡，自摸鸡，放铳鸡\n{m.group(1)}还说，他有四个鸡，我说，坐东鸡，坐西鸡，坐南鸡，坐北鸡\n{m.group(1)}又说，他有三个鸡，我说，上一打鸡，这一打鸡，下一打鸡\n{m.group(1)}又说，他有两个鸡，我说，子家鸡 亲家鸡\n{m.group(1)}最后说，他有一个鸡，我说，{m.group(1)}就是鸡")
                senderid = event.sender.id
                if botname == "":
                    return
                if botname in event.message_chain:
                    if senderid in black_list['user']:
                        return await bot.send(event, getreply(reply=replydata['blackuser']))
                    msg = msg.replace(f"{botname}", "", 1)
                    if settings['r18talk']:
                        if senderid in admin:
                            for k, v in replydata['r18'].items():
                                if k in msg:
                                    return await bot.send(event, getreply(reply=v, rndimg=True))
                            return await bot.send(event, getreply(reply=replydata['mismatch']['admin'], rndimg=True))
                        else:
                            for k, v in replydata['common'].items():
                                if k in msg:
                                    return await bot.send(event, getreply(reply=v, rndimg=True))
                            return await bot.send(event, getreply(reply=replydata['mismatch']['common'], rndimg=True))
                    else:
                        for k, v in replydata['common'].items():
                            if k in msg:
                                return await bot.send(event, getreply(reply=v, rndimg=True))
                        return await bot.send(event, getreply(reply=replydata['mismatch']['common'], rndimg=True))


    # 亲亲

    @bot.on(GroupMessage)
    async def on_kiss(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(亲|亲亲)\s*@?(\w+)?\s*', msg.strip())
        if m:
            if At in event.message_chain:
                operator_id = event.sender.id
                target_id = event.message_chain.get_first(At).target
                if operator_id == target_id:
                    return await bot.send(event, getreply(text="请不要自交", rndimg=True))
                else:
                    await kiss(operator_id=operator_id, target_id=target_id)
                    await bot.send(event, MessageChain(
                        Image(path=f'./images/KissKiss/temp/tempKiss-{operator_id}-{target_id}.gif')))


    # 摸头

    @bot.on(GroupMessage)
    async def on_group_message(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(摸|摸摸|摸头)\s*@?(\w+)?\s*$', msg.strip())
        if m:
            if At in event.message_chain:
                target = event.message_chain.get_first(At).target
                await petpet(target)
                await bot.send(event, MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
            # else:
            #     target = m.group(2)
            #     await petpet(target)
            #     await bot.send(event, MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))


    @bot.on(MessageEvent)
    async def imgoperate(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}bw\s*([\u4e00-\u9fa5\w%&,;:=?!\s$\x22，。？！\d]+)\s*$', msg.strip())
        if m and event.message_chain.has(Image):
            try:
                img = event.message_chain.get_first(Image)
                imgname = img.image_id
                await img.download(filename=f'./images/tempimg/{imgname}')
                makebwimg(imgname, m.group(1))
                await bot.send(event, MessageChain([Image(path=f'./images/tempimg/{imgname}')]))
                deletesource(imgname)
            except Exception as e:
                print(e)
                rootLogger.exception(e)


    @bot.on(MessageEvent)
    async def getremakeimg(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(重开|remake)\s*(\d+)?\s*(\w+)?\s*$', msg.strip())
        if m:
            senderid = event.sender.id
            if m.group(2):
                basic_score = int(m.group(2))
            else:
                basic_score = 30
            if m.group(3):
                worlddifficulty = m.group(3)
            else:
                worlddifficulty = None
            create_remakeimg(senderid, basic_score=basic_score, worlddifficulty=worlddifficulty)
            await bot.send(event, MessageChain(Image(path=f'./images/Remake/{senderid}.png')))
        return


    # 签到获取积分

    @bot.on(MessageEvent)
    async def signin(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}\s*签到\s*$', msg.strip())
        if m:
            signmsg = siginin(event.sender.id)
            return await bot.send(event, getreply(text=signmsg, rndimg=True))


    # 查询积分

    @bot.on(GroupMessage)
    async def getuserscore(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}\s*获取当前积分\s*$', msg.strip())
        if m:
            scoremsg = getscore(
                userid=event.sender.id)
            return await bot.send(event, getreply(text=scoremsg, rndimg=True))


    # 戳一戳 出发摸头

    @bot.on(NudgeEvent)
    async def Nudgepetpet(event: NudgeEvent):

        # await bot.send(event,NudgeEvent(from_id=bot.qq,target=event.from_id))
        sender = event.from_id

        if sender == bot.qq:
            return
        if (not settings['silence']) or settings['nudgereply']:
            if event.subject.kind == 'Group':
                if not (event.subject.id in silencegroup or event.subject.id in disnudgegroup):
                    target = event.target
                    if target == bot.qq:
                        if sender in admin:
                            await bot.send_group_message(event.subject.id,
                                                         MessageChain(
                                                             [Plain(random.choice(replydata['nudgedata']['admin']))]))
                            await petpet(target)
                            await bot.send_group_message(event.subject.id,
                                                         MessageChain(
                                                             Image(
                                                                 path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
                        else:
                            if random.random() < 0.2:
                                if random.random() < 0.2:
                                    await bot.send_group_message(event.subject.id,
                                                                 getreply(
                                                                     reply=replydata['nudgedata']['supernudgereply'],
                                                                     rndimg=True))
                                    for i in range(10):
                                        await bot.send_nudge(subject=event.subject.id, target=sender, kind='Group')
                                    return
                                else:
                                    await bot.send_nudge(subject=event.subject.id, target=sender, kind='Group')
                                    return await bot.send_group_message(event.subject.id,
                                                                        getreply(
                                                                            reply=replydata['nudgedata']['nudgereply'],
                                                                            rndimg=True))
                            else:
                                return await bot.send_group_message(event.subject.id,
                                                                    MessageChain(
                                                                        [Plain(
                                                                            random.choice(
                                                                                replydata['nudgedata']['other']))]))
                    else:
                        await petpet(target)
                        await bot.send_group_message(event.subject.id,
                                                     MessageChain(
                                                         Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
        return


    # 群龙王
    # @bot.on(GroupEvent)
    # async def dradonchange(event: MemberHonorChangeEvent):
    #     if event.member.id == bot.qq:
    #         if event.honor == 'TALKACTIVE':
    #             if event.action == 'lose':
    #                 await bot.send(event, "呜呜，我的龙王被抢走惹~")
    #             else:
    #                 await bot.send(event, "我是水群冠军！")

    scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器


    @bot.on(Shutdown)
    def stop_scheduler(_):
        scheduler.shutdown(True)  # 结束定时器


    # 雀魂对局记录轮询器

    @scheduler.scheduled_job(CronTrigger(hour='*', minute=f'*'))
    async def paiputimer():
        minute_now = datetime.datetime.now().minute
        hour_now = datetime.datetime.now().hour
        second_now = datetime.datetime.now().second
        if minute_now == 0:
            if hour_now == 0:
                global rootLogger, qqlogger
                rootLogger = create_logger(config['loglevel'])
                qqlogger = getQQlogger()

            if 7 < hour_now < 23:
                for groupid in alarmclockgroup:
                    if groupid != 0 and type(groupid) == int:
                        await bot.send_group_message(groupid, getreply(text=f"准点报时: {datetime.datetime.now().hour}:00",
                                                                       rndimg=True))
                        if hour_now == 22:
                            await bot.send_group_message(groupid, getreply(text="晚上10点了，大家可以休息了", rndimg=True))
        if minute_now % config["searchfrequency"] == 0:
            if settings['autogetpaipu']:
                print(f"开始查询,当前时间{hour_now}:{minute_now}:{second_now}")
                try:
                    if settings['asyreptile']:
                        # await asyth_auto()
                        await asyth_all()
                        await asyqh_autopaipu()
                    else:
                        await th_autopaipu()
                        await th_broadcastmatch()
                        await qh_autopaipu()
                except sqlite3.OperationalError as e:
                    logging.warning("自动查询失败,可能是数据库不存在或者表不存在,牌谱查询将关闭")
                    logging.warning(f'{e}')
                    settings['autogetpaipu'] = False
                except websockets.exceptions.ConnectionClosedError as e:
                    logging.error(f'websockets发生错误{e}')
                    logging.exception(e)
                    exit(0)
                print(f"查询结束,当前时间{hour_now}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}")


    bot.run(port=17580)
