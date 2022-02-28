import os
import random
import re
import asyncio
import datetime

import yaml

from mirai.models import MemberHonorChangeEvent, GroupEvent, MemberJoinEvent, NudgeEvent
from mirai import FriendMessage, Mirai, WebSocketAdapter, GroupMessage, Plain, Startup, Shutdown, At, MessageChain, \
    Image
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import plugin.MajSoulInfo.majsoulinfo as qhinfo
import plugin.jupai.holdup
import plugin.Petpet.gif
import plugin.KissKiss.Kisskiss

whiteList = []
black_userlist = []
mute_grouplist = []
admin = []
welcomeinfo = []
config = {}
settings = {}
alarmclockgroup = []
commandpre = ""
if __name__ == '__main__':

    if not os.path.exists("./database"):
        os.mkdir("./database")
    if not os.path.exists("./images"):
        os.mkdir("./images")
    if not os.path.exists("./data"):
        os.mkdir("./data")
    if not os.path.exists("./log"):
        os.mkdir("./log")

    try:
        with open(r'./config.yml') as f:
            config = yaml.safe_load(f)
            print(config)
            whiteList = config['whitelist']
            mute_grouplist = config['mutegrouplist']
            settings = config['settings']
            welcomeinfo = config['welcomeinfo']
            alarmclockgroup = config['alarmclockgroup']
            commandpre = config['commandpre']
    except Exception as e:
        print("文件打开错误，尝试生成初始文件中...")
        with open(r'./config.yml', 'w') as f:
            yaml.dump(dict(admin=[], whitelist=[], blacklist=[], mutegrouplist=[],
                           welcomeinfo=["欢迎%ps%加入%gn%"], alarmclockgroup=[], commandpre="",
                           settings=dict(autogetpaipu=True, autowelcome=True)), f,
                      allow_unicode=True)
            print("默认文件生成完成，请重新启动。")
            exit(0)

    bot = Mirai(
        qq=123465,  # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key='NekoRabi', host='localhost', port=17280
        )
    )


    async def autopaipu():
        nowtime = datetime.datetime.now()
        print(f"开始查询,当前时间{nowtime.hour}:{nowtime.minute}:{nowtime.second}")
        result = qhinfo.autoQueryPaipu()
        for info in result:
            for group in info['groups']:
                await bot.send_group_message(group, info['text'])
        nowtime = datetime.datetime.now()
        print(f"查询结束,当前时间{nowtime.hour}:{nowtime.minute}:{nowtime.second}")
        return


    # 欢迎
    @bot.on(MemberJoinEvent)
    async def welcome(event: MemberJoinEvent) -> None:
        if settings['autowelcome']:
            personid = event.member.id
            personname = event.member.member_name
            groupname = event.member.group.name
            info: str = random.choice(welcomeinfo)
            info = info.replace('%ps%', personname)
            info = info.replace('%gn%', groupname)
            msg = MessageChain([
                At(personid),
                Plain(f" {info}")
            ])
            await bot.send_group_message(event.member.group.id, msg)
            await plugin.Petpet.gif.petpet(personid)
            await bot.send_group_message(event.subject.id,
                                         MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{personid}.gif')))
            return

    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')


    @bot.on(FriendMessage)
    async def ping(event: FriendMessage):
        if event.message_chain.has("ping"):
            print("ping了一下")
            await bot.send(event, "pong!")
        return


    @bot.on(GroupMessage)
    async def shaochongtixing(event: GroupMessage):
        senderid = event.sender.id
        if senderid in whiteList:
            return
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}色图\s*(\w+)\s*$', msg.strip())
        if m:
            if random.random() * 100 < 10:
                await bot.send(event, [At(event.sender.id), "能不能少冲点"])
        return


    """雀魂相关"""


    @bot.on(GroupMessage)
    async def getmajsoulhelp(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(help|雀魂帮助)\s*$', msg.strip())
        if m:
            return await bot.send(event, MessageChain([
                At(event.sender.id),
                Plain(" 指令帮助 ()内为可选项,[]为必选项,{}为可用参数:\n"
                      " qhpt / 雀魂分数 [玩家名] :查询该玩家的段位分\n"
                      " qhsl / 雀魂十连 ({限时/常驻}) :来一次模拟雀魂十连\n"
                      " qhadd / 雀魂添加关注 [玩家名] :将一个玩家添加至自动查询，有新对局记录时会广播\n"
                      " qhgetwatch / 雀魂获取本群关注 :获取本群所有的雀魂关注的玩家\n"
                      " qhdel / 雀魂删除关注 [玩家名] :将一个玩家从自动查询中移除，不再自动广播对局记录\n"
                      " 雀魂最近对局 [玩家名] [{3/4}] ({1-5}) :查询一个玩家最近n场3/4人对局记录\n"
                      " qhinfo / 雀魂玩家详情 [玩家名] [{3/4}] :查询一个玩家的详细数据\n"
                      " 举牌 [内容] :将内容写在举牌小人上发出来\n")
            ]))


    # 查分
    @bot.on(GroupMessage)
    async def qhpt(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhpt|雀魂分数)\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, qhinfo.query(m.group(2)))
        return


    @bot.on(GroupMessage)
    async def getsomepaipu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}雀魂最近对局\s*(\w+)\s*([0-9]+)*\s*([0-9]+)*\s*$', msg.strip())

        if m:
            playername = m.group(1)
            searchtype = m.group(2)
            if searchtype:
                if searchtype.strip() not in ['3', '4']:
                    await bot.send(event, '牌局参数有误，请输入 3 或 4')
                    return
                if m.group(3):
                    searchnumber = int(m.group(3))
                    if 0 < searchnumber < 5:
                        # playerid =
                        # qhinfo.getsomepaipu(m.group())
                        await bot.send(event, qhinfo.getsomepaipu(playername=playername.strip(), type=searchtype,
                                                                  counts=searchnumber))
                        return
                    else:
                        await bot.send(event, "牌局数量有误，最多支持5场牌局")
                        return
                else:
                    await bot.send(event, qhinfo.getsomepaipu(playername=playername.strip(), type=searchtype.strip()))


    @bot.on(GroupMessage)
    async def getplayerdetails(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(fr'^{commandpre}(qhinfo|雀魂玩家详情)\s*(\w+)\s*(\w+)*\s*(\w+)*\s*$', msg.strip())
        if m:
            playername = m.group(2)
            selecttype = m.group(3)
            selectlevel = m.group(4)
            if selectlevel:
                pass
            else:
                await bot.send(event, qhinfo.getplayerdetail(playername=playername, selecttype=selecttype))


    # 将一个雀魂用户加入某群的关注
    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhadd|雀魂添加关注)\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, qhinfo.addwatch(m.group(2), event.sender.group.id))


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
            await bot.send(event, qhinfo.getallwatcher(event.group.id))


    # 删除某群雀魂关注
    @bot.on(GroupMessage)
    async def delwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr'^{commandpre}(qhdel|雀魂删除关注)\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, qhinfo.removewatch(playername=m.group(2), groupid=event.sender.group.id))


    # 来一发雀魂十连
    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'^{commandpre}(qhsl|雀魂十连)\s*(\w+)*\s*$', msg.strip())
        if m:
            if m.group(2):
                if m.group(2) == '限时':
                    result = qhinfo.drawcards(up=True)
                    meanmessage = MessageChain([
                        At(event.sender.id),
                        Plain("\n 抽卡结果:\n"),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][0]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][1]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][2]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][3]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][4]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][5]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][6]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][7]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][8]}')),
                        Image(path=str(f'./plugin/MajSoulInfo/{result["results"][9]}'))
                    ])
                    await bot.send(event, meanmessage)
                    await bot.send(event, MessageChain([
                        At(event.sender.id),
                        Plain(result['resultsmsg'])
                    ]))
                elif m.group(2) == '常驻':
                    result = qhinfo.drawcards(up=False)
                    meanmessage = MessageChain([
                        At(event.sender.id),
                        Plain("\n 抽卡结果:\n"),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][0]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][1]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][2]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][3]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][4]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][5]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][6]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][7]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][8]}')),
                        Image(path=str(f'./plugin/MajSoulInfo/{result["results"][9]}'))
                    ])
                    await bot.send(event, meanmessage)
                    await bot.send(event, MessageChain([
                        At(event.sender.id),
                        Plain(result['resultsmsg'])
                    ]))
                else:
                    await bot.send(event, MessageChain([At(event.sender.id), Plain('参数输入有误，请输入“限时”或“常驻”，此次十连将输出常驻')]))
                    result = qhinfo.drawcards(up=False)
                    meanmessage = MessageChain([
                        At(event.sender.id),
                        Plain("\n 抽卡结果:\n"),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][0]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][1]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][2]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][3]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][4]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][5]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][6]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][7]}')),
                        Image(
                            path=str(f'./plugin/MajSoulInfo/{result["results"][8]}')),
                        Image(path=str(f'./plugin/MajSoulInfo/{result["results"][9]}'))
                    ])
                    await bot.send(event, meanmessage)
                    await bot.send(event, MessageChain([
                        At(event.sender.id),
                        Plain(result['resultsmsg'])
                    ]))
            else:
                result = qhinfo.drawcards(up=False)
                meanmessage = MessageChain([
                    At(event.sender.id),
                    Plain("\n 抽卡结果:\n"),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][0]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][1]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][2]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][3]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][4]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][5]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][6]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][7]}')),
                    Image(
                        path=str(f'./plugin/MajSoulInfo/{result["results"][8]}')),
                    Image(path=str(f'./plugin/MajSoulInfo/{result["results"][9]}'))
                ])
                await bot.send(event, meanmessage)
                await bot.send(event, MessageChain([
                    At(event.sender.id),
                    Plain(result['resultsmsg'])
                ]))


    '''通用功能'''

    '''随机搞怪回复'''


    @bot.on(GroupMessage)
    async def duideduide(event: GroupMessage):
        if len(event.message_chain[Plain]) == 1:
            msg = str(event.message_chain[Plain][0]).strip()
            if msg in ['正确的', '错误的', '辩证的', '哦对的对的', '啊对对对']:
                if random.random()*100 < 30:
                    await bot.send(event, random.choice(['正确的', '错误的', '辩证的', '对的对的', '不对的', '哦对的对的']))


    '''创建举牌文字'''


    @bot.on(GroupMessage)
    async def jupai(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr'''^{commandpre}举牌\s*([\u4e00-\u9fa5\w%&',;=?!^.$\x22，。？！]+)\s*$''', msg.strip())
        if m:
            if len(m.group(1)) > 40:
                await bot.send(event, "最多支持做40个字的举牌哦~")
            plugin.jupai.holdup.imgoutput(m.group(1))
            message_chain = MessageChain([
                await Image.from_local('./images/jupai.png')
            ])
            await bot.send(event, message_chain)


    # 添加白名单
    @bot.on(GroupMessage)
    async def addwhitelist(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        m = re.match(r'^addwhitelist\s*(\w+)\s*$', msg.strip())
        if m:
            if userid in admin and userid not in whiteList:

                whiteList.append(m.group(1))
                print(whiteList)
                with open(r'./config.yml', 'w') as file:
                    yaml.dump(
                        dict(admin=admin, whitelist=whiteList, blacklist=black_userlist, mutegrouplist=mute_grouplist,
                             welcomeinfo=welcomeinfo, alarmclockgroup=alarmclockgroup, commandpre=commandpre,
                             settings=settings), file,
                        allow_unicode=True)
                print(m)
                return await bot.send(event, "添加成功")
            else:
                return await bot.send(event, "添加失败,用户已存在")


    '''随机打断、复读、嘲讽'''


    @bot.on(GroupMessage)
    async def on_group_message(event: GroupMessage):
        count = random.random() * 100
        msg = event.message_chain[Plain]
        senderid = event.sender.id
        if senderid in whiteList:
            return
        if str(msg) == "?" and count > 70:
            print(f"在{event.group.name}群,复读了一次?")
            return await bot.send(event, "?")
        if count < 0.2:
            print(f"在{event.group.name}群,打断一次{msg}")
            return await bot.send(event, random.choice(["¿", "Lux is watching you!"]))
        elif count < 0.5:
            print(f"在{event.group.name}群,打断一次{msg}")
            return await bot.send(event, "?")
        elif count < 1:
            print(f"在{event.group.name}群,复读一次{msg}")
            return await bot.send(event, event.message_chain)

    # 亲亲
    @bot.on(GroupMessage)
    async def on_kiss(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^(亲|亲亲)\s*@?(\w+)?\s*', msg.strip())
        if m:
            if At in event.message_chain:
                operator_id = event.sender.id
                target_id = event.message_chain.get_first(At).target
                if operator_id == target_id:
                    return await bot.send(event, MessageChain([Plain("请不要自交~😋")]))
                else:
                    await plugin.KissKiss.Kisskiss.kiss(operator_id=operator_id,target_id=target_id)
                    await bot.send(event,MessageChain(Image(path=f'./images/KissKiss/temp/tempKiss-{operator_id}-{target_id}.gif')))

    # 摸头
    @bot.on(GroupMessage)
    async def on_group_message(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^(摸|摸摸)\s*@?(\w+)?\s*$', msg.strip())
        if m:
            if At in event.message_chain:
                target = event.message_chain.get_first(At).target
                await plugin.Petpet.gif.petpet(target)
                await bot.send(event, MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
            else:
                target = m.group(2)
                await plugin.Petpet.gif.petpet(target)
                await bot.send(event, MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))

    # 戳一戳 出发摸头
    @bot.on(NudgeEvent)
    async def petpet(event: NudgeEvent):
        target = event.target
        await plugin.Petpet.gif.petpet(target)
        await bot.send_group_message(event.subject.id,
                                     MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
        # msg = "".join(map(str, event.message_chain[Plain]))
        # m = re.match(r'^(摸)\s*(\w+)\s*$', msg.strip())
        # if m:
        #     targetid = event


    # 群龙王
    # @bot.on(GroupEvent)
    # async def dradonchange(event: MemberHonorChangeEvent):
    #     if event.member.id == bot.qq:
    #         if event.honor == 'TALKACTIVE':
    #             if event.action == 'lose':
    #                 await bot.send(event, "呜呜，我的龙王被抢走惹~")
    #             else:
    #                 await bot.send(event, "我是水群冠军！")

    _task = None


    @bot.on(Startup)
    async def start_scheduler(_):

        async def timer():
            today_finished = False  # 设置变量标识今天是会否完成任务，防止重复发送
            while True:
                await asyncio.sleep(1)
                now = datetime.datetime.now()
                if now.hour == 7 and now.minute == 30 and not today_finished:  # 每天早上 7:30 发送早安
                    for group in alarmclockgroup:
                        await bot.send_group_message(group, "早上好")
                    today_finished = True
                if now.hour == 7 and now.minute == 31:
                    today_finished = False  # 早上 7:31，重置今天是否完成任务的标识

        global _task
        _task = asyncio.create_task(timer())


    @bot.on(Shutdown)
    async def stop_scheduler(_):
        # 退出时停止定时任务
        if _task:
            _task.cancel()


    scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器


    @bot.on(Shutdown)
    def stop_scheduler(_):
        scheduler.shutdown(True)  # 结束定时器


    # 雀魂对局记录轮询器
    @scheduler.scheduled_job(CronTrigger(hour='*', minute='0/6'))
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
            await autopaipu()


    bot.run(port=17580)
