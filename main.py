import re
import asyncio
import datetime

from plugin import *

from mirai.models import MemberJoinEvent, NudgeEvent
from mirai import FriendMessage, GroupMessage, Plain, Startup, Shutdown, At, MessageChain, \
    Image, MessageEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

if __name__ == '__main__':

    create_folders()
    config = load_config()

    black_list = dict(user=[], group=[])
    black_list['user'] = config['blacklist']
    black_list['group'] = config['mutegrouplist']
    whiteList = config['whitelist']
    admin:list = config['admin']
    master = config['master']
    settings = config['settings']
    botname = config['botconfig']['botname']
    replydata = load_replydata()
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


    # 自动获取雀魂牌谱
    async def autopaipu():
        nowtime = datetime.datetime.now()
        print(f"开始查询,当前时间{nowtime.hour}:{nowtime.minute}:{nowtime.second}")
        result = autoQueryPaipu()
        for info in result:
            for group in info['groups']:
                await bot.send_group_message(group, info['text'])
        nowtime = datetime.datetime.now()
        print(f"查询结束,当前时间{nowtime.hour}:{nowtime.minute}:{nowtime.second}")
        return


    # 自动获取天凤对局
    async def thautopaipu():
        print("开始查询天风结算信息")
        msglist = autoget_th_match()
        print(f'正在进行的对局有{msglist}')
        for msgobj in msglist:
            for group in msgobj['groups']:
                await bot.send_group_message(group, msgobj['msg'])
        return

    # 自动广播天凤对局开始信息
    async def thbroadcastmatch():
        print("开始查询天风对局信息")
        msglist = auto_get_th_matching()
        for msgobj in msglist:
            for group in msgobj['groups']:
                await bot.send_group_message(group, msgobj['msg'])
        return


    def get_groupsender_permission(event: GroupMessage):
        return event.sender.permission


    def is_havingadmin(event: GroupMessage):
        if event.sender.permission == "MEMBER":
            return False
        return True


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


    @bot.on(GroupMessage)
    async def addadmin(event: GroupMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}addadmin\s*(\d+)\s*$", msg.strip())
            if m:
                if m.group(1) in admin:
                    admin.append(m.group(1))

                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    return await bot.send(event, MessageChain(Plain(f" 已将 {m.group(1)} 添加为机器人管理员")))
        return


    @bot.on(GroupMessage)
    async def deladmin(event: GroupMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}deladmin\s*(\d+)\s*$", msg.strip())
            if m:
                if not m.group(1) in admin:
                    admin.remove(m.group(1))

                    with open(r'./config.yml', 'w') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    return await bot.send(event, MessageChain(Plain(f" 已将 {m.group(1)} 从机器人管理员中移出")))
        return

    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')


    # PING

    @bot.on(FriendMessage)
    async def ping(event: FriendMessage):
        if event.message_chain.has("ping"):
            print("ping了一下")
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


    @bot.on(MessageEvent)
    async def setu(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(色图|涩图|setu)\s*(\w+)?\s*$', msg.strip())
        if m:
            print(f"收到来自{event.sender.id}的色图请求")
            if random.random() * 100 < 10:
                print(f"发出对{event.sender.id}的少冲提醒")
                await bot.send(event, [At(event.sender.id), " 能不能少冲点啊"])
            else:
                if settings['setu']:
                    imginfo = getsetu(m.group(2).strip())
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
            return await bot.send(event, MessageChain([
                Plain(" 指令帮助 ()内为可选项,[]为必选项,{}为可用参数:\n"
                      " qhpt / 雀魂分数 [玩家名] :查询该玩家的段位分\n"
                      " qhsl / 雀魂十连 ({限时/常驻}) :来一次模拟雀魂十连\n"
                      " qhadd / 雀魂添加关注 [玩家名] :将一个玩家添加至雀魂自动查询，有新对局记录时会广播\n"
                      " qhgetwatch / 雀魂获取本群关注 :获取本群所有的雀魂关注的玩家\n"
                      " qhdel / 雀魂删除关注 [玩家名] :将一个玩家从雀魂自动查询中移除，不再自动广播对局记录\n"
                      " 雀魂最近对局 [玩家名] [{3/4}] ({1-5}) :查询一个玩家最近n场3/4人对局记录\n"
                      " qhinfo / 雀魂玩家详情 [玩家名] [{3/4}] :查询一个玩家的详细数据\n"
                      " qhyb / 雀魂月报 [玩家名] [{3/4}] [yyyy-mm] :查询一个玩家yy年mm月的3/4麻对局月报"
                      " thadd / 天凤添加关注 [玩家名] :将一个玩家添加指天凤的自动查询，有新对局会广播\n"
                      " thdel / 天凤删除关注 [玩家名] :将一个玩家从天凤自动查询中移除，不再自动广播对局记录\n"
                      " 举牌 [内容] :将内容写在举牌小人上发出来\n"
                      " 亲/亲亲 @用户 : 两人互亲\n"
                      " 摸/摸摸/摸头 @用户 : 摸某人头\n"
                      " 重开 / remake : 异世界转生\n"
                      " 项目地址 : 获取项目链接")
            ]))


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
                if command == 'pt':
                    if not group in qhsettings['disptgroup']:
                        qhsettings['disptgroup'].append(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                        # return await bot.send(event,f'查分功能禁用成功')


    @bot.on(GroupMessage)
    async def enableqhplugin(event: GroupMessage):
        # 匹配指令
        if is_havingadmin(event) or event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(fr'^{commandpre}enable\s*(\w+)\s*$', msg.strip())
            if m:
                command = m.group(1)
                group = event.group.id
                if command == 'pt':
                    if group in qhsettings['disptgroup']:
                        qhsettings['disptgroup'].remove(group)
                        with open(r'./config.yml', 'w') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            # return await bot.send(event, f'查分功能启用成功')


    # 查分

    @bot.on(GroupMessage)
    async def qhpt(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhpt|雀魂分数)\s*(\w+)\s*$', msg.strip())
        if m:
            if qhsettings['qhpt'] and not event.group.id in qhsettings['disptgroup']:
                await bot.send(event, query(m.group(2)))
            return


    @bot.on(GroupMessage)
    async def getsomepaipu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr'^{commandpre}雀魂最近对局\s*(\w+)\s*([0-9]+)*\s*([0-9]+)*\s*$', msg.strip())

        if m:
            playername = m.group(1)
            searchtype = m.group(2)
            if searchtype:
                if searchtype.strip() not in ['3', '4']:
                    await bot.send(event, '牌局参数有误，请输入 3 或 4')
                    return
                if m.group(3):
                    searchnumber = int(m.group(3))
                    if 0 < searchnumber < 11:
                        await bot.send(event, getsomeqhpaipu(playername=playername.strip(),
                                                             type=searchtype,
                                                             counts=searchnumber))
                        return
                    else:
                        await bot.send(event, "牌局数量有误，最多支持10场牌局")
                        return
                else:
                    await bot.send(event, getsomepaipu(playername=playername.strip(),
                                                       type=searchtype.strip()))


    @bot.on(GroupMessage)
    async def getplayerdetails(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(
            fr'^{commandpre}(qhinfo|雀魂玩家详情)\s*(\w+)\s*(\w+)*\s*(\w+)*\s*(\w+)*\s*$', msg.strip())
        if m:
            playername = m.group(2)
            selecttype = m.group(3)
            model = m.group(4)
            selectlevel = m.group(5)
            if selectlevel:
                pass
            else:
                if model == None:
                    model = '基本'
                await bot.send(event, getplayerdetail(playername=playername,
                                                      selecttype=selecttype,
                                                      model=model))


    @bot.on(GroupMessage)
    async def getmondetails(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(
            fr'^{commandpre}(qhyb|雀魂月报)\s*(\w+)\s*(3|4)\s*([0-9]{{1,4}})\-([0-9]{{1,2}})\s*$', msg.strip())
        if m:
            playername = m.group(2)
            selecttype = m.group(3)
            year = m.group(4)
            month = m.group(5)
            await bot.send(event, MessageChain([Plain(
                getmonthreport(playername=playername, selecttype=selecttype, year=year, month=month))]))
            # await bot.send(event,MessageChain([Plain(f"你要查询的是{playername}在{year}年{month}月的{selecttype}麻的雀魂月报吗?\n这个功能还没做哦~")]))
        return


    # 将一个雀魂用户加入某群的关注

    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhadd|雀魂添加关注)\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, addwatch(m.group(2), event.group.id))


    # @bot.on(GroupMessage)
    # async def refresh(event: GroupMessage):
    #     # msg = "".join(map(str, event.message_chain[Plain]))
    #     # # 匹配指令
    #     # m = re.match(r'^刷新雀魂订阅\s*(\w+)\s*$', msg.strip())
    #     if event.message_chain.has("刷新雀魂关注"):
    #         # qhinfo.autoQueryPaipu()
    #         print('手动刷新一次')
    #         await autopaipu()

    # 获取某群的雀魂关注人员

    @bot.on(GroupMessage)
    async def getqhwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhgetwatch|雀魂获取本群关注)\s*$', msg.strip())
        if m:
            await bot.send(event, getallwatcher(event.group.id))


    # 删除某群雀魂关注

    @bot.on(GroupMessage)
    async def delwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhdel|雀魂删除关注)\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event,
                           removewatch(playername=m.group(2), groupid=event.group.id))


    # 来一发雀魂十连

    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(qhsl|雀魂十连)\s*(\w+)*\s*$', msg.strip())
        if m:
            if m.group(2):
                if m.group(2) == '限时':
                    result = drawcards(userid=event.sender.id, up=True)
                    if result['error']:
                        return await bot.send(event, MessageChain([At(event.sender.id), Plain(result['resultsmsg'])]))
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
                elif m.group(2) == '常驻':
                    result = drawcards(userid=event.sender.id, up=False)
                    if result['error']:
                        return await bot.send(event, MessageChain([At(event.sender.id), Plain(result['resultsmsg'])]))
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
                    await bot.send(event, MessageChain([At(event.sender.id), Plain('参数输入有误，请输入“限时”或“常驻”，此次十连将输出常驻')]))
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
                # return await bot.send(event, MessageChain([
                #     At(event.sender.id),
                #     Plain(result['resultsmsg'])
                # ]))
        return


    '''天凤相关'''


    @bot.on(GroupMessage)
    async def addtenhouwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(thadd|天凤添加关注)\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, addthwatch(m.group(2), event.group.id))


    @bot.on(GroupMessage)
    async def deltenhouwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(thdel|天凤删除关注)\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event,
                           removethwatch(playername=m.group(2), groupid=event.group.id))


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
            if not event.group.id in silencegroup:
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
            fr'''^{commandpre}举牌\s*([\u4e00-\u9fa5\w%&',;:=?!^.$\x22，。？！]+)\s*$''', msg.strip())
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
                    if not event.group.id in silencegroup:
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
                    if not event.group.id in norepeatgroup:
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
            if not event.group.id in silencegroup:
                if not event.group.id in norepeatgroup:
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
            if not event.group.id in silencegroup:
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
                '''if event.message_chain[1].type == 'App':
                    app = event.message_chain[1].as_json()
                    url = app['meta']['detail_1']['preview']
                    img_url = f'http://{url}'''
                message_chain = MessageChain([Plain(text=bvid), Image(url=img_url)])
                return await bot.send(event, message_chain)


    @bot.on(GroupMessage)
    async def diyreply(event: GroupMessage):
        if not settings['silence']:
            if not event.group.id in silencegroup:
                msg = "".join(map(str, event.message_chain[Plain]))
                senderid = event.sender.id
                if botname == "":
                    return
                if botname in event.message_chain:
                    if senderid in black_list['user']:
                        return await bot.send(event, random.choice(replydata['blackuser']))
                    msg = msg.replace(f"{botname}", "", 1)
                    if settings['r18talk']:
                        if senderid in admin:
                            for k, v in replydata['r18'].items():
                                if k in msg:
                                    return await bot.send(event, random.choice(v))
                            return await bot.send(event, random.choice(replydata['mismatch']['admin']))
                        else:
                            for k, v in replydata['common'].items():
                                if k in msg:
                                    return await bot.send(event, random.choice(v))
                            return await bot.send(event, random.choice(replydata['mismatch']['common']))
                    else:
                        for k, v in replydata['common'].items():
                            if k in msg:
                                return await bot.send(event, random.choice(v))
                        return await bot.send(event, random.choice(replydata['mismatch']['common']))


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
                    return await bot.send(event, MessageChain([Plain("请不要自交~")]))
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
    async def getremakeimg(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(重开|remake)\s*$', msg.strip())
        if m:
            senderid = event.sender.id
            create_remakeimg(senderid)
            await bot.send(event, MessageChain(Image(path=f'./images/Remake/{senderid}.png')))
        return


    # 签到获取积分

    @bot.on(MessageEvent)
    async def signin(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}\s*签到\s*$', msg.strip())
        if m:
            signmsg = siginin(event.sender.id)
            return await bot.send(event, MessageChain([Plain(signmsg)]))


    # 查询积分

    @bot.on(GroupMessage)
    async def getuserscore(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}\s*获取当前积分\s*$', msg.strip())
        if m:
            scoremsg = getscore(
                userid=event.sender.id)
            return await bot.send(event, MessageChain([Plain(scoremsg)]))


    # 戳一戳 出发摸头

    @bot.on(NudgeEvent)
    async def Nudgepetpet(event: NudgeEvent):
        if (not settings['silence']) or settings['nudgereply']:
            if event.subject.kind == 'Group':
                if not (event.subject.id in silencegroup or event.subject.id in disnudgegroup):
                    target = event.target
                    if target == bot.qq:
                        sender = event.from_id
                        if sender in admin:
                            await bot.send_group_message(event.subject.id,
                                                         MessageChain(
                                                             [Plain(random.choice(replydata['nudgedate']['admin']))]))
                            await petpet(target)
                            await bot.send_group_message(event.subject.id,
                                                         MessageChain(
                                                             Image(
                                                                 path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
                        else:
                            await bot.send_group_message(event.subject.id,
                                                         MessageChain(
                                                             [Plain(random.choice(replydata['nudgedate']['other']))]))
                    else:
                        await petpet(target)
                        await bot.send_group_message(event.subject.id,
                                                     MessageChain(
                                                         Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))


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

    @scheduler.scheduled_job(CronTrigger(hour='*', minute=f'0/{config["searchfrequency"]}'))
    async def paiputimer():
        minute_now = datetime.datetime.now().minute
        hour_now = datetime.datetime.now().hour
        if minute_now == 0:
            if 7 < hour_now < 23:
                for groupid in alarmclockgroup:
                    if groupid != 0 and type(groupid) == int:
                        await bot.send_group_message(groupid, f"准点报时: {datetime.datetime.now().hour}:00")
                        if hour_now == 22:
                            await bot.send_group_message(groupid, f"晚上10点了，大家可以休息了")
        if settings['autogetpaipu']:
            try:
                await autopaipu()
            except sqlite3.OperationalError:
                print("自动查询失败,可能是数据库不存在或者表不存在,牌谱查询将关闭")
                settings['autogetpaipu'] = False
            await thautopaipu()
            await thbroadcastmatch()


    bot.run(port=17580)
