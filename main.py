import random
import re
import asyncio
import datetime
import time

import func_timeout.exceptions
import yaml
from func_timeout import func_set_timeout

from mirai.models import MemberHonorChangeEvent, GroupEvent, MemberJoinEvent
from mirai import FriendMessage, Mirai, WebSocketAdapter, GroupMessage, Plain, Startup, Shutdown, At, MessageChain, \
    Image
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import plugin.MajSoulInfo.majsoulinfo as qhinfo
import plugin.jupai.holdup
import sqlite3

group_id_list = [566415871, 736711628, 696897899, 796128056]

whiteList = []
black_userlist = []
mute_grouplist = []
admin = [1215791340]
time_out_sec = 180
autogetpaipu = False
welcomeinfo = []
config = {}

if __name__ == '__main__':
    bot = Mirai(
        qq=3384437741,  # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key='xyshu123', host='localhost', port=17280
        )
    )

    try:
        with open(r'./config.yml') as f:
            config = yaml.safe_load(f)
            print(config)
            time_out_sec = config['timeout']
            whiteList = config['whitelist']
            mute_grouplist = config['mutegrouplist']
            autogetpaipu = config['settings']['autogetpaipu']
            welcomeinfo = config['welcomeinfo']
    except:
        print("文件打开错误，尝试生成初始文件中...")
        with open(r'./config.yml', 'w') as f:
            yaml.dump(dict(admin=[1215791340], whitelist=[1215791340], blacklist=[0], mutegrouplist=[0],
                           welcomeinfo=["欢迎%ps%加入%gn%"], timeout=180, settings=dict(autogetpaipu=False)), f,
                      allow_unicode=True)
            print("默认文件生成完成，请重新启动。")
            exit(0)


    @func_set_timeout(timeout=time_out_sec)
    async def autopaipu():
        print("开始查询", end="\t")
        nowtime = datetime.datetime.now()
        result = qhinfo.autoQueryPaipu()
        for info in result:
            for group in info['groups']:
                await bot.send_group_message(group, info['text'])
        print(f"查询结束,当前时间{nowtime.hour}:{nowtime.minute}:{nowtime.second}")
        return time.time()


    # 欢迎
    @bot.on(MemberJoinEvent)
    async def welcome(event: MemberJoinEvent):
        personid = event.member.id
        personname = event.member.member_name
        groupname = event.member.group.name
        info: str = random.choice(welcomeinfo)
        info = info.replace('%ps%', personname)
        info = info.replace('%gn%', groupname)
        msg = MessageChain([
            At(personid),
            Plain(info)
        ])
        await bot.send_group_message(event.member.group.id, msg)


    @bot.on(GroupMessage)
    async def getlocaltime(event: GroupMessage):
        msg = str(event.message_chain).strip()
        if msg == "获取时间":
            return bot.send(event, str(time.time()))


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
        m = re.match(r'^色图\s*(\w+)\s*$', msg.strip())
        if m:
            if random.randint(0, 100) < 10:
                await bot.send(event, [At(event.sender.id), "能不能少冲点"])


    """雀魂相关"""


    @bot.on(GroupMessage)
    async def getsomepaipu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'''^查询最近对局\s*(\w+)\s*(\w+)\s*([0-9]+)\s*$''')
        if m:
            if m.group(2) not in ['3', '4']:
                await bot.send(event, '牌局参数有误，请输入 3 或 4')
                return
            if 0 < int(m.group(3)) < 5:
                playername = m.group(1)
                # playerid =
                return
                # qhinfo.getsomepaipu(m.group())
            else:
                await bot.send(event, "牌局数量有误，最多支持5场牌局")


    # @bot.on(FriendMessage)
    # async def on_friend_message(event: FriendMessage):
    #     msg = "".join(map(str, event.message_chain[Plain]))
    #     # 匹配指令
    #     m = re.match(r'^查询雀魂\s*(\w+)\s*$', msg.strip())
    #     if m:
    #         await bot.send(event, qhinfo.query(m.group(1)))
    #     return

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
                with open(r'./config.yml', 'w') as f:
                    yaml.dump(dict(admin=admin, whitelist=whiteList, blacklist=black_userlist, mutegrouplist=mute_grouplist,
                                   welcomeinfo=welcomeinfo, timeout=time_out_sec, settings=dict(autogetpaipu=autogetpaipu)), f,
                              allow_unicode=True)
                print(m)
                return await bot.send(event, "添加成功")
            else:
                return await bot.send(event, "添加失败,用户已存在")


    # 查分
    @bot.on(GroupMessage)
    async def qhpt(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^qhpt\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, qhinfo.query(m.group(1)))
        return


    # 将一个雀魂用户加入某群的关注
    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^添加雀魂关注\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, qhinfo.addwatch(m.group(1), event.sender.group.id))


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
        if event.message_chain.has("获取本群雀魂关注"):
            await bot.send(event, qhinfo.getallwatcher(event.group.id))


    # 删除某群雀魂关注
    @bot.on(GroupMessage)
    async def delwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^删除雀魂关注\s*(\w+)\s*$', msg.strip())
        if m:
            await bot.send(event, qhinfo.removewatch(playername=m.group(1), groupid=event.sender.group.id))


    # 来一发雀魂十连
    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^雀魂十连\s*(\w+)\s*$', msg.strip())
        if m:
            if m.group(1) == '限时':
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
            elif m.group(1) == '常驻':
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
        elif event.message_chain.has('雀魂十连'):
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
                if random.randint(0, 10) < 3:
                    await bot.send(event, random.choice(['正确的', '错误的', '辩证的', '对的对的', '不对的', '哦对的对的']))


    '''创建举牌文字'''


    @bot.on(GroupMessage)
    async def jupai(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'''^举牌\s*([\u4e00-\u9fa5\w%&',;=?!^.$\x22，。？！]+)\s*$''', msg.strip())
        if m:
            if len(m.group(1)) > 40:
                await bot.send(event, "最多支持做40个字的举牌哦~")
            plugin.jupai.holdup.imgoutput(m.group(1))
            message_chain = MessageChain([
                await Image.from_local('./images/jupai.png')
            ])
            await bot.send(event, message_chain)


    @bot.on(GroupMessage)
    def on_group_message(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(r'^摸\s*(\w+)\s*$', msg.strip())
        if At(bot.qq) in event.message_chain and m:
            print("bot被{0}摸了一次".format(str(event.sender.id)))
            # return bot.send(event, [At(event.sender.id), '你在叫我吗？'])


    '''随机打断、复读、嘲讽'''


    @bot.on(GroupMessage)
    async def on_group_message(event: GroupMessage):
        count = random.randint(0, 1000)
        msg = event.message_chain[Plain]
        senderid = event.sender.id
        if senderid in whiteList:
            return
        if str(msg) == "?" and count > 700:
            print(f"在{event.group.name}群,复读了一次?")
            return await bot.send(event, "?")
        if count < 2:
            print(f"在{event.group.name}群,打断一次{msg}")
            return await bot.send(event, random.choice(["¿", "Lux is watching you!"]))
        elif count < 5:
            print(f"在{event.group.name}群,打断一次{msg}")
            return await bot.send(event, "?")
        elif count < 10:
            print(f"在{event.group.name}群,复读一次{msg}")
            return await bot.send(event, event.message_chain)


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
                    for group in group_id_list:
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
                await bot.send_group_message(566415871, f"准点报时: {datetime.datetime.now().hour}:00")
                if hour_now == 22:
                    await bot.send_group_message(566415871, f"晚上10点了，大家可以休息了，不报时了")
        if autogetpaipu:
            try:
                await autopaipu()
            except func_timeout.exceptions.FunctionTimedOut:
                print("执行查询超时")


    bot.run(port=17580)
