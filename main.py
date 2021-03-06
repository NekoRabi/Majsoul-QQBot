import logging
from typing import Union

import nest_asyncio
import re
import requests
import websockets.exceptions

from plugin import *
from utils.bufferpool import *
from utils.text_to_voice import VoiceCreater
from utils.file_cleaner import cleaner
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai import FriendMessage, GroupMessage, Plain, Startup, Shutdown, At, MessageChain, \
    Image, MessageEvent, Voice, AtAll
from mirai.models import MemberJoinEvent, NudgeEvent, Forward, ForwardMessageNode, FlashImage, MessageComponent

if __name__ == '__main__':

    nest_asyncio.apply()
    create_folders()
    config = load_config()
    replydata = load_replydata()
    create_helpimg()
    commands_map = load_commands()
    cmdbuffer = commandcache()
    qqlogger = getQQlogger()
    rootLogger = create_logger(config['loglevel'])

    black_list = dict(user=config['blacklist'], group=config['mutegrouplist'])
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
    nudgeconfig = config['nudgeconfig']
    stfinder = SetuFinder(botname)
    vc = None

    if settings['voice']:
        vc = VoiceCreater(setting=config['voicesetting'])

    bot = create_bot(config)

    if master not in admin:
        admin.append(master)
    print(f"机器人{botname}启动中\tQQ : {bot.qq}")


    async def sendMsgChain(msg: Union[MessageChain, str, MessageComponent], event: MessageEvent = None,
                           grouptarget: int = None, friendtarget: int = None, errortext: str = None):
        res = 0
        if msg is not MessageChain:
            msg = MessageChain(msg)
        errtext = "消息发送失败"
        imgSendErrText = f"图片发送失败,这肯定不是{botname}的问题!"
        if errortext:
            errtext = errortext
            imgSendErrText = errortext
        onlyImg = False
        msgComponentTypeList = []

        for component in msg:
            msgComponentTypeList.append(component.type)
        if msgComponentTypeList == ['Image']:
            onlyImg = True
        if event:
            res = await bot.send(event, msg)
            if res == -1 and not onlyImg:
                # if Image in msg and not onlyImg :
                #     msg[Image] = None
                await bot.send(event, errtext)

        elif grouptarget:
            res = await bot.send_group_message(grouptarget, msg)
            if res == -1 and not onlyImg:
                await bot.send_group_message(grouptarget, errtext)
            # errtext += f'消息类型:GroupMessageEvent,消息目标:{grouptarget}'
        elif friendtarget:
            res = await bot.send_friend_message(friendtarget, msg)
            if res == -1 and not onlyImg:
                await bot.send_group_message(friendtarget, errtext)
            # errtext += f'消息类型:FriendMessageEvent,消息目标:{friendtarget}'
        if res == -1 and onlyImg:
            if grouptarget:
                await bot.send_group_message(grouptarget, makeMsgChain(text=imgSendErrText, rndimg=True))
            elif event:
                await bot.send(event, makeMsgChain(text=imgSendErrText, rndimg=True))
            elif friendtarget:
                await bot.send_friend_message(friendtarget, makeMsgChain(text=imgSendErrText, rndimg=True))

        return


    async def asyqh_autopaipu():
        print("开始查询雀魂信息")
        result = await majsoul.asygetqhpaipu()
        print(result)
        for msgobj in result:
            for group in msgobj['groups']:
                b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
                # await bot.send_group_message(group, msgobj['msg'])
                await sendMsgChain(grouptarget=group, msg=makeMsgChain(imgbase64=b64))
        return


    async def asyth_all():
        print("开始查询天凤信息")
        result = await tenhou.asygetTH()
        print(result)
        for msgobj in result:
            for group in msgobj['groups']:
                b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
                # await bot.send_group_message(group, msgobj['msg'])
                await sendMsgChain(grouptarget=group, msg=makeMsgChain(imgbase64=b64))
        return


    def makeMsgChain(reply: list = None, text: str = None, rndimg: bool = False, imgpath: str = None,
                     imgurl: str = None, imgbase64=None,
                     at: int = None, atall=False) -> MessageChain:
        msgchain = []
        if at:
            msgchain.append(At(at))
            msgchain.append(Plain(" "))
        elif atall:
            msgchain.append(AtAll())
            msgchain.append(Plain(" "))
        if reply:
            msgchain.append(Plain(random.choice(reply)))
        elif text:
            msgchain.append(Plain(text))
        if reply or text:
            msgchain.append(Plain(random.choice(replydata['suffix'])))
        if rndimg:
            msgchain.append(Plain("\n"))
            msgchain.append(
                Image(path=f"./data/reply/img/{replydata['replyimgpath']}/{random.choice(replydata['img'])}"))
        if imgpath:
            if reply or text:
                msgchain.append(Plain("\n"))
            msgchain.append(
                Image(path=f"{imgpath}"))
        if imgbase64:
            if reply or text:
                msgchain.append(Plain("\n"))
            msgchain.append(Image(base64=imgbase64))
        if imgurl:
            if reply or text:
                msgchain.append(Plain("\n"))
            msgchain.append(Image(url=imgurl))
        return MessageChain(msgchain)


    def get_groupsender_permission(event: GroupMessage):
        return event.sender.permission


    def is_havingadmin(event: GroupMessage):
        if event.sender.id in admin:
            return True
        elif event.sender.permission == "MEMBER":
            return False
        return True


    def getbase64voice(text):
        voice = dict(error=False, file=None, errmsg=None)
        if vc:
            voice['file'] = vc.getbase64voice(text=text)
        else:
            voice['error'] = True
        return voice


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
            info = info.replace('%ps%', personname).replace('%gn%', groupname)
            await petpet(personid)
            await sendMsgChain(
                makeMsgChain(text=info, at=personid), grouptarget=event.member.group.id)
            await bot.send(event, Image(path=f'./images/PetPet/temp/tempPetPet-{personid}.gif'))
            # await sendMsgChain(makeMsgChain(imgpath=f'./images/PetPet/temp/tempPetPet-{personid}.gif'),
            #                    grouptarget=event.member.group.id)
            return


    @bot.on(FriendMessage)
    async def freshqhpaipu(event: FriendMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}freshqh\s*$", msg.strip())
            if m:
                print("牌谱刷新中")
                await sendMsgChain(msg="牌谱刷新中", event=event)
                await asyqh_autopaipu()


    @bot.on(FriendMessage)
    async def addadmin(event: FriendMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}{commands_map['sys']['addadmin']}", msg.strip())
            if m:
                qqid = int(m.group(1))
                if qqid not in admin:
                    admin.append(qqid)
                    with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    await sendMsgChain(event=event, msg=f"已将 {m.group(1)} 添加为机器人管理员")
                else:
                    await sendMsgChain(event=event, msg=f"{m.group(1)} 已经是管理员了")

        else:
            await sendMsgChain(event=event, msg=makeMsgChain(text="抱歉,您无权这么做哦", rndimg=True))

        return


    @bot.on(FriendMessage)
    async def deladmin(event: FriendMessage):
        if event.sender.id == master:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}{commands_map['sys']['deladmin']}", msg.strip())
            if m:
                qqid = int(m.group(1))
                if qqid in admin:
                    admin.remove(qqid)
                    with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    return await sendMsgChain(event=event, msg=f"已将 {m.group(1)} 从机器人管理员中移出")
                else:
                    return await sendMsgChain(event=event, msg=f"{m.group(1)} 不是再管理员了")
        else:
            await bot.send(event, makeMsgChain(text="抱歉,您无权这么做哦", rndimg=True))
        return


    @bot.on(FriendMessage)
    async def sayhello(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return sendMsgChain(event=event, msg='Hello, World!')


    '''获取日志'''
    '''{commands_map['sys']['']}'''


    @bot.on(FriendMessage)
    async def getsyslog(event: FriendMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}{commands_map['sys']['log']}", msg.strip())
            if m:
                return await bot.send(event, "日志功能开发中")
            #     if m.group(1):
            #         if m.group(2):
            #             return
            #         else:
            #             return
            #     else:
            #         return
            # return


    # PING

    @bot.on(FriendMessage)
    async def ping(event: FriendMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}{commands_map['sys']['ping']}", msg.strip())
            if m:
                rootLogger.info("ping了一下")
                await bot.send(event, "pong!")
        return


    # 强制复读

    @bot.on(FriendMessage)
    async def sendmsgtogroup(event: FriendMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}{commands_map['sys']['sendmsgtogroup']}", msg.strip())
            if m:
                return await bot.send_group_message(int(m.group(1)), m.group(2))


    @bot.on(GroupMessage)
    async def groupAt(event: GroupMessage):
        if event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(
                fr"^{commandpre}at::\s*([\u4e00-\u9fa5\w%&',@;=?!^.$\x22，。？！]+)\s*$", msg.strip())
            if m:
                if At in event.message_chain:
                    target = event.message_chain.get_first(At).target
                    return await bot.send(event, MessageChain([At(target), Plain(f" {m.group(1)}")]))


    # 色图
    @bot.on(GroupMessage)
    async def enablesetu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{commands_map['setu']['enable']}", msg.strip())
        if m:
            if event.sender.id in admin:
                groupid = event.group.id
                if groupid in config['setugroups']:
                    await bot.send(event, makeMsgChain(text="本群已开启色图", rndimg=True))
                else:
                    config['setugroups'].append(groupid)
                    with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    await bot.send(event, makeMsgChain(text="色图开启成功", rndimg=True))


    @bot.on(GroupMessage)
    async def disablesetu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))

        m = re.match(
            fr"^{commandpre}{commands_map['setu']['disable']}", msg.strip())
        if m:
            if event.sender.id in admin:
                groupid = event.group.id
                if groupid in config['setugroups']:
                    config['setugroups'].remove(groupid)
                    with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    await bot.send(event, makeMsgChain(text="色图已关闭", rndimg=True))
                else:
                    await bot.send(event, makeMsgChain(text="本群色图已关闭", rndimg=True))


    @bot.on(GroupMessage)
    async def getsomesetu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m1 = re.match(
            fr"^{commandpre}{commands_map['setu']['getsetu1']}", msg.strip())
        m2 = re.match(
            fr"^{commandpre}{commands_map['setu']['getsetu2']}", msg.strip())
        if m1:
            if random.random() * 100 < 10:
                # print(f"发出对{event.sender.id}的少冲提醒")
                # await bot.send(event, [At(event.sender.id), " 能不能少冲点啊，这次就不给你发了"])
                pass
            else:
                if settings['setu'] and event.group.id in config['setugroups']:
                    if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'setu')):
                        return bot.send(event, makeMsgChain(text="你冲的频率太频繁了,休息一下吧", rndimg=True, at=event.sender.id))
                    try:
                        imginfo = await stfinder.getsetu(
                            m1.group(2), groupid=event.group.id)
                        if imginfo['FoundError']:
                            return await sendMsgChain(event=event,
                                                      msg=makeMsgChain(at=event.sender.id, text=imginfo['ErrorMsg']))
                        await sendMsgChain(event=event, msg=makeMsgChain(imgurl=imginfo['url']))
                    except Exception as e:
                        print(f"色图请求失败:{e}")
                        await bot.send(event, MessageChain([Plain(f"出错了!这肯定不是{botname}的问题!")]))
        elif m2:
            if random.random() * 100 < 10:
                # print(f"发出对{event.sender.id}的少冲提醒")
                # await bot.send(event, [At(event.sender.id), " 能不能少冲点啊，这次就不给你发了"])
                pass
            else:
                if settings['setu'] and event.group.id in config['setugroups']:
                    if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'setu')):
                        return bot.send(event, makeMsgChain(at=event.sender.id, text="你冲的频率太频繁了,休息一下吧", rndimg=True))

                    try:
                        imginfo = await stfinder.getsetu(
                            m2.group(2), event.group.id, m2.group(1))
                        if imginfo['FoundError']:
                            return await bot.send(event, makeMsgChain(at=event.sender.id, text=imginfo['ErrorMsg']))
                        await sendMsgChain(event=event, msg=makeMsgChain(imgurl=imginfo['url']))
                        # await bot.send(event, MessageChain([Image(url=imginfo['url'])]))
                    except Exception as e:
                        print(f"色图请求失败:{e}")
                        await bot.send(event, MessageChain([Plain(f"出错了!这肯定不是{botname}的问题!")]))
        return


    @bot.on(MessageEvent)
    async def getsyshelp(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{commands_map['sys']['help']}", msg.strip())
        if m and settings['help']:
            # if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'help')):
            #     return bot.send(event, makeMsgChain()(text="帮助文档刚刚才发过哦~", rndimg=True, at=event.sender.id))
            return await bot.send(event, Image(path="./images/grouphelp.png"))


    '''获取机器人信息'''


    @bot.on(FriendMessage)
    async def getbotinfo(event: FriendMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        m = re.match(fr"^{commandpre}{commands_map['sys']['getbotinfo']}", msg.strip())
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
            # 匹配指令
            m = re.match(fr"^{commandpre}{commands_map['sys']['silence_all']}", msg.strip())
            if m:
                if m.group(1).lower() == 'on' or m.group(1).lower() == 'true':
                    settings['silence'] = True
                    with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, allow_unicode=True)
                else:
                    settings['silence'] = False
                    with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, allow_unicode=True)


    # 单群沉默 - 从群聊沉默

    @bot.on(GroupMessage)
    async def begroupsilencebygroup(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        if userid in admin:
            m = re.match(fr"^{commandpre}{commands_map['sys']['silence_group']}", msg.strip())
            if m:
                if m.group(1).lower() == 'on' or m.group(1).lower() == 'true':
                    if event.group.id not in silencegroup:
                        silencegroup.append(event.group.id)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                else:
                    if event.group.id in silencegroup:
                        silencegroup.remove(event.group.id)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)


    # 关闭复读

    @bot.on(GroupMessage)
    async def norepeatbygroup(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        if userid in admin:
            m = re.match(fr"^{commandpre}{commands_map['sys']['repeat']}", msg.strip())
            if m:
                if m.group(1).lower() in ['on', 'true']:
                    print(f'已将{event.group.id}的复读关闭')
                    if event.group.id not in norepeatgroup:
                        norepeatgroup.append(event.group.id)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                else:
                    if event.group.id in norepeatgroup:
                        print(f'已将{event.group.id}的复读开启')
                        norepeatgroup.remove(event.group.id)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)


    # 添加白名单

    @bot.on(GroupMessage)
    async def addwhitelist(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        userid = event.sender.id
        # 匹配指令
        m = re.match(fr"^{commandpre}{commands_map['sys']['addwhitelist']}", msg.strip())
        if m:
            if userid in admin and userid not in whiteList:

                whiteList.append(int(m.group(1)))
                with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
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
        m = re.match(fr"^{commandpre}{commands_map['sys']['addblacklist']}", msg.strip())
        if m:
            if userid in admin:
                if int(m.group(1)) in admin:
                    return await bot.send(event, "请不要将管理员加入黑名单")
                black_list['user'].append(int(m.group(1)))
                print(black_list['user'])
                with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
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
        m = re.match(fr"^{commandpre}{commands_map['sys']['delblacklist']}", msg.strip())
        if m:
            if userid in admin:
                delperson = int(m.group(1))
                if delperson in black_list['user']:
                    black_list['user'].remove(delperson)
                    with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, allow_unicode=True)
                    return await bot.send(event, "删除成功")
                else:
                    return await bot.send(event, "删除失败,用户不存在")


    # 获取项目地址

    @bot.on(MessageEvent)
    async def getprojectlink(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}项目地址\s*$", msg.strip())
        if m:
            return await bot.send(event, MessageChain([Plain(
                "Github : https://github.com/NekoRabi/Majsoul-QQBot\n"
                "Gitee : https://gitee.com/Syaro/Majsoul-QQBot\n"
                "如果觉得好可以点个star⭐")]))

            # 与机器人互动


    # 签到获取积分

    @bot.on(MessageEvent)
    async def signUp(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sys']['signin']}", msg.strip())
        if m:
            success, signmsg = signup(event.sender.id)
            if success:
                card = tarotcards.drawcards(userid=event.sender.id)[0]
                return await bot.send(event, makeMsgChain(at=event.sender.id, text=signmsg, imgbase64=card.imgcontent))
            else:
                return await bot.send(event, makeMsgChain(at=event.sender.id, text=signmsg, rndimg=True))


    # 查询积分

    @bot.on(MessageEvent)
    async def getuserscore(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sys']['getscore']}", msg.strip())
        if m:
            scoremsg = getscore(
                userid=event.sender.id)
            return await bot.send(event, makeMsgChain(text=scoremsg, rndimg=True))


    """雀魂相关"""


    # 禁用功能

    @bot.on(GroupMessage)
    async def disableqhplugin(event: GroupMessage):
        # 匹配指令
        if is_havingadmin(event) or event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(fr"^{commandpre}{commands_map['majsoul']['disable']}", msg.strip())
            if m:
                commandname = m.group(2)
                group = event.group.id
                if commandname in ['qhpt', '雀魂分数', '雀魂pt']:
                    if group not in qhsettings['disptgroup']:
                        qhsettings['disptgroup'].append(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'查分功能禁用成功')
                elif commandname in ['qhpaipu', '雀魂最近对局']:
                    if group not in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].append(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')
                elif commandname in ['qhinfo', '雀魂玩家详情']:
                    if group not in qhsettings['disinfogroup']:
                        qhsettings['disinfogroup'].append(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'雀魂玩家详情功能禁用成功')
                elif commandname in ['qhsl', '雀魂十连']:
                    if group not in qhsettings['disybgroup']:
                        qhsettings['disybgroup'].append(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'模拟十连功能禁用成功')
                elif commandname in ['qhyb', '雀魂月报']:
                    if group not in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].append(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')
                else:
                    return await bot.send(event, '无此功能,请重新输入参数')


    # 启用功能

    @bot.on(GroupMessage)
    async def enableqhplugin(event: GroupMessage):
        # 匹配指令
        if is_havingadmin(event) or event.sender.id in admin:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(fr"^{commandpre}{commands_map['majsoul']['enable']}", msg.strip())
            if m:
                commandname = m.group(2)
                group = event.group.id
                if commandname in ['qhpt', '雀魂分数', '雀魂pt']:
                    if group in qhsettings['disptgroup']:
                        qhsettings['disptgroup'].remove(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'查分功能启用成功')
                elif commandname in ['qhpaipu', '雀魂最近对局']:
                    if group in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].remove(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')
                elif commandname in ['qhinfo', '雀魂玩家详情']:
                    if group in qhsettings['disinfogroup']:
                        qhsettings['disinfogroup'].remove(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'雀魂玩家详情功能禁用成功')
                elif commandname in ['qhsl', '雀魂十连']:
                    if group in qhsettings['disybgroup']:
                        qhsettings['disybgroup'].remove(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'模拟十连功能禁用成功')
                elif commandname in ['qhyb', '雀魂月报']:
                    if group in qhsettings['dispaipugroup']:
                        qhsettings['dispaipugroup'].remove(group)
                        with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file, allow_unicode=True)
                            return await bot.send(event, f'牌谱查询功能禁用成功')
                else:
                    return await bot.send(event, '无此功能,请重新输入参数')


    # 查分

    @bot.on(GroupMessage)
    async def qhpt(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['qhpt']}", msg.strip())
        if m:
            if qhsettings['qhpt'] and event.group.id not in qhsettings['disptgroup']:

                if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'qhpt')):
                    return bot.send(event, makeMsgChain(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
                if m.group(3):
                    if m.group(4):
                        await sendMsgChain(event=event,
                                           msg=majsoul.getcertaininfo(m.group(2), m.group(3), int(m.group(4))))
                    else:
                        await sendMsgChain(msg=majsoul.getcertaininfo(m.group(2), m.group(3)), event=event)
                else:
                    result = majsoul.query(m.group(2))
                    if result['error']:
                        # await bot.send(event, result['msg'])
                        await sendMsgChain(msg=result['msg'], event=event)
                    else:
                        await sendMsgChain(msg=Image(path=f'./images/MajsoulInfo/qhpt{m.group(2)}.png'), event=event,
                                           errortext=result['msg'])
                        # await bot.send(event, Image(path=f'./images/MajsoulInfo/qhpt{m.group(2)}.png'))
            return


    @bot.on(GroupMessage)
    async def getrecentqhpaipu(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['qhpaipu']}", msg.strip())
        if m:
            if qhsettings['qhpaipu'] and event.group.id not in qhsettings['dispaipugroup']:

                if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'qhpaipu')):
                    return sendMsgChain(event=event,
                                        msg=makeMsgChain(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
                playername = m.group(2)
                searchtype = m.group(3)
                searchnumber = 5
                if searchtype:
                    if searchtype not in ['3', '4']:
                        return await sendMsgChain(event=event, msg='牌局参数有误，请输入 3 或 4')

                    if m.group(4):
                        searchnumber = int(m.group(4))
                        if not 0 < searchnumber < 11:
                            return await bot.send(event, "牌局数量有误，最多支持10场牌局")
                    result = await majsoul.getsomeqhpaipu(playername=playername, type=searchtype,
                                                          counts=searchnumber)
                    if not result['err']:
                        await sendMsgChain(event=event,
                                           msg=makeMsgChain(imgbase64=result['img64']), errortext=result['msg'])
                    else:
                        await sendMsgChain(event=event, msg=result['msg'])


    @bot.on(GroupMessage)
    async def getplayerdetails(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['qhinfo']}", msg.strip())
        if m:
            if qhsettings['qhinfo'] and event.group.id not in qhsettings['disinfogroup']:

                if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'qhinfo')):
                    return bot.send(event, makeMsgChain(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
                playername = m.group(2)
                selecttype = m.group(3)
                model = m.group(4)
                selectlevel = m.group(5)
                if selectlevel:
                    pass
                else:
                    if model is None:
                        model = '基本'
                    detail = majsoul.getplayerdetail(
                        playername=playername, selecttype=selecttype, model=model)
                    if detail['error']:
                        await bot.send(event, detail['msg'])
                    else:
                        res = await bot.send(event, Image(path=f'./images/MajsoulInfo/detail{playername}.png'))
                        if res == -1:
                            await bot.send(event, detail['msg'])
        return


    @bot.on(GroupMessage)
    async def getmondetails(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['qhyb']}", msg.strip())
        if m:
            if qhsettings['qhyb'] and event.group.id not in qhsettings['disybgroup']:
                if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'qhyb')):
                    return bot.send(event, makeMsgChain(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
                playername = m.group(2)
                selecttype = m.group(3)
                year = m.group(4)
                month = m.group(5)
                report = majsoul.getmonthreport(
                    playername=playername, selecttype=selecttype, year=year, month=month)
                if report['error']:
                    await bot.send(event, report['msg'])
                else:
                    try:
                        res_id = await bot.send(event,
                                                MessageChain([Image(path=f'./images/MajsoulInfo/yb{playername}.png')]))
                        # print(res_id)
                        if res_id == -1:
                            print(f"图片yb{playername}.png发送失败，尝试发送文本")
                            await bot.send(event, report['msg'])
                    except Exception as e:
                        print(e)
                        await bot.send_friend_message(master,
                                                      makeMsgChain(text=f"消息发送出现问题了,快看看后台.群聊id:{event.group.id}"))
                    # await bot.send(event,makeMsgChain()(imgbase64=report['imgbase64']))
        return


    # 获取某群的雀魂关注人员

    @bot.on(GroupMessage)
    async def getqhwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['getwatch']}", msg.strip())
        if m:
            await bot.send(event, majsoul.getallwatcher(event.group.id))


    # 将一个雀魂用户加入某群的关注

    @bot.on(GroupMessage)
    async def addmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['addwatch']}", msg.strip())
        if m:
            if event.group.id not in qhsettings['disautoquerygroup']:
                # if is_havingadmin(event):
                #     await bot.send(event, addwatch(m.group(2), event.group.id))
                # else:
                #     await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))
                await bot.send(event, majsoul.addwatch(m.group(2), event.group.id))


    # 删除某群雀魂关注

    @bot.on(GroupMessage)
    async def delmajsoulwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['delwatch']}", msg.strip())
        if m:
            if event.group.id not in qhsettings['disautoquerygroup']:
                # if is_havingadmin(event):
                #     await bot.send(event,
                #                    removewatch(playername=m.group(2), groupid=event.group.id))
                # else:
                #     await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))
                await bot.send(event, majsoul.removewatch(m.group(2), event.group.id))
        return


    # 来一发雀魂十连

    @bot.on(GroupMessage)
    async def qhdrawcards(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['qhsl']}", msg.strip())
        if m:
            if qhsettings['qhsl'] and event.group.id not in qhsettings['disslgroup']:
                if m.group(2):
                    if m.group(2) in ['限时', '限定', 'up', 'UP']:
                        result = majsoul.drawcards(userid=event.sender.id, up=True)
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
                        result = majsoul.drawcards(userid=event.sender.id, up=False)
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
                        result = majsoul.drawcards(userid=event.sender.id, up=False)
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
                    result = majsoul.drawcards(userid=event.sender.id, up=False)
                    if result['error']:
                        return await bot.send(event, MessageChain([At(event.sender.id), Plain(result['resultsmsg'])]))
                    mergeimgs(
                        result.get('results'), event.sender.id)
                    await bot.send(event, MessageChain([
                        At(event.sender.id),
                        Plain("\n 抽卡结果:\n"),
                        Image(path=f"./images/MajSoulInfo/{event.sender.id}.png")]))
            else:
                return await bot.send(event, makeMsgChain(text="此群已禁用模拟抽卡"))
        return


    @bot.on(GroupMessage)
    async def getmyqhdrawcards(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['getmyqhsl']}", msg.strip())
        if m:
            return await bot.send(event, majsoul.getmycard(event.sender.id))


    @bot.on(GroupMessage)
    async def clearmajsoulwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['clearwatch']}", msg.strip())
        if m:
            if is_havingadmin(event):
                await bot.send(event, majsoul.clearallwatch(groupid=event.group.id))
            else:
                await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))


    # 添加昵称
    @bot.on(GroupMessage)
    async def qhaddtag(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['tagon']}", msg.strip())
        if m:
            if not m.group(3):
                return await sendMsgChain(event=event, msg=makeMsgChain(text='请输入你要添加tag哦'))
            if is_havingadmin(event):
                await bot.send(event,
                               majsoul.tagonplayer(playername=m.group(2), tagname=m.group(3), userid=event.sender.id,
                                                   groupid=event.group.id))
            else:
                await sendMsgChain(event=event, msg=makeMsgChain(at=event.sender.id, text='抱歉，只有管理员才能这么做'))


    # 删除昵称
    @bot.on(GroupMessage)
    async def qhdeltag(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['tagoff']}", msg.strip())
        if m:
            if is_havingadmin(event):
                tagnames = None
                if m.group(3):
                    tagnames = m.group(3)
                await bot.send(event, majsoul.tagoffplayer(playername=m.group(2), groupid=event.group.id,
                                                           userid=event.sender.id, tagname=tagnames))
            else:
                await bot.send(event, makeMsgChain(at=event.sender.id, text='抱歉，只有管理员才能这么做'))


    # 昵称操作
    @bot.on(GroupMessage)
    async def qhtagoperate(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['tagopeartion']}", msg.strip())
        ope_type = 'add'
        p1 = 'xyshu'
        p2 = '帅哥'
        if m:
            if is_havingadmin(event):
                if m.group(2):
                    ope_type = m.group(2).lower()
                print(ope_type)
                if ope_type not in ['cut', 'copy']:
                    return
                if m.group(3):
                    p1 = m.group(3)
                if m.group(4):
                    p2 = m.group(4)
                # result = majsoul.tagonplayer(playername=p1, tagname=p2, userid=event.sender.id,
                #                     groupid=event.group.id)
                result = majsoul.tag_C_operation(event.group.id, p1, p2, ope_type)
                await sendMsgChain(makeMsgChain(text=result), event)


    # 获取所有tag

    @bot.on(GroupMessage)
    async def qhlisttag(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['majsoul']['taglist']}", msg.strip())
        if m:
            target = m.group(2)
            searchtype = 'playername'
            if target:
                if target.startswith('tag=') or target.startswith('tagname='):
                    target = target.split('=', 2)[1]
                    searchtype = 'tagname'
            await sendMsgChain(event=event, msg=makeMsgChain(
                text=majsoul.getalltags(event.group.id, target=target, searchtype=searchtype)))


    # 天凤相关

    @bot.on(GroupMessage)
    async def ranktenhouplayer(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['tenhou']['thpt']}", msg.strip())
        if m:
            if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'thpt')):
                return sendMsgChain(event=event,
                                    msg=makeMsgChain(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
            reset = True
            if m.group(3):
                reset = m.group(3)
                if reset.lower().startswith('reset=') and len(reset) > 6:
                    reset = reset[6:-1]
                    if reset.lower() == 'true':
                        reset = True
                    else:
                        reset = False
                else:
                    reset = False
            result = await tenhou.getthpt(m.group(2), reset)
            await sendMsgChain(makeMsgChain(imgbase64=result['img64']), event=event,errortext=result['msg'])
            # await bot.send(event, tenhou.getthpt(m.group(2), reset))


    @bot.on(GroupMessage)
    async def addtenhouwatch(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['tenhou']['addwatch']}", msg.strip())
        if m:
            if is_havingadmin(event):
                await sendMsgChain(event=event, msg=makeMsgChain(text=tenhou.addthwatch(m.group(2), event.group.id)))
            else:
                await sendMsgChain(event=event, msg=makeMsgChain(text='抱歉，此权限需要管理员', at=event.sender.id))


    @bot.on(GroupMessage)
    async def deltenhouwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['tenhou']['delwatch']}", msg.strip())
        if m:
            if is_havingadmin(event):
                await bot.send(event,
                               tenhou.removethwatch(playername=m.group(2), groupid=event.group.id))
            else:
                await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))


    @bot.on(GroupMessage)
    async def cleartenhouwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['tenhou']['clearwatch']}", msg.strip())
        if m:
            if is_havingadmin(event):
                await bot.send(event, tenhou.clearthwatch(groupid=event.group.id))
            else:
                await bot.send(event, MessageChain([At(event.sender.id), Plain(" 抱歉，只有管理员才能这么做哦")]))


    @bot.on(GroupMessage)
    async def gettenhouwatcher(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(fr"^{commandpre}{commands_map['tenhou']['getwatch']}", msg.strip())
        if m:
            await bot.send(event, tenhou.getthwatch(event.group.id))


    # 添加昵称
    # @bot.on(GroupMessage)
    # async def thaddtag(event: GroupMessage):
    #     msg = "".join(map(str, event.message_chain[Plain]))
    #     m = re.match(fr"^{commandpre}{commands_map['tenhou']['tagon']}", msg.strip())
    #     if m:
    #         if not m.group(3):
    #             return await sendMsgChain(event=event, msg=makeMsgChain(text='请输入你要添加tag哦'))
    #         if is_havingadmin(event):
    #             await bot.send(event,
    #                            tenhou.tagonplayer(playername=m.group(2), tagname=m.group(3), userid=event.sender.id,
    #                                                groupid=event.group.id))
    #         else:
    #             await sendMsgChain(event=event, msg=makeMsgChain(at=event.sender.id, text='抱歉，只有管理员才能这么做'))
    #
    #
    #
    # # 删除昵称
    # @bot.on(GroupMessage)
    # async def thdeltag(event: GroupMessage):
    #     msg = "".join(map(str, event.message_chain[Plain]))
    #     m = re.match(fr"^{commandpre}{commands_map['tenhou']['tagoff']}", msg.strip())
    #     if m:
    #         if is_havingadmin(event):
    #             tagnames = None
    #             if m.group(3):
    #                 tagnames = m.group(3)
    #             await bot.send(event, tenhou.tagoffplayer(playername=m.group(2), groupid=event.group.id,
    #                                                        userid=event.sender.id, tagname=tagnames))
    #         else:
    #             await bot.send(event, makeMsgChain(at=event.sender.id, text='抱歉，只有管理员才能这么做'))
    #
    #
    # # 昵称操作
    # @bot.on(GroupMessage)
    # async def thtagoperate(event: GroupMessage):
    #     msg = "".join(map(str, event.message_chain[Plain]))
    #     m = re.match(fr"^{commandpre}{commands_map['tenhou']['tagopeartion']}", msg.strip())
    #     ope_type = 'add'
    #     p1 = 'xyshu'
    #     p2 = '帅哥'
    #     if m:
    #         if is_havingadmin(event):
    #             if m.group(2):
    #                 ope_type = m.group(2).lower()
    #             print(ope_type)
    #             if ope_type not in ['cut', 'copy']:
    #                 return
    #             if m.group(3):
    #                 p1 = m.group(3)
    #             if m.group(4):
    #                 p2 = m.group(4)
    #             # result = majsoul.tagonplayer(playername=p1, tagname=p2, userid=event.sender.id,
    #             #                     groupid=event.group.id)
    #             result = tenhou.tag_C_operation(event.group.id, p1, p2, ope_type)
    #             await sendMsgChain(makeMsgChain(text=result), event)
    #
    #
    # # 获取所有tag
    #
    # @bot.on(GroupMessage)
    # async def thlisttag(event: GroupMessage):
    #     msg = "".join(map(str, event.message_chain[Plain]))
    #     m = re.match(fr"^{commandpre}{commands_map['tenhou']['taglist']}", msg.strip())
    #     if m:
    #         target = m.group(2)
    #         searchtype = 'playername'
    #         if target:
    #             if target.startswith('tag=') or target.startswith('tagname='):
    #                 target = target.split('=', 2)[1]
    #                 searchtype = 'tagname'
    #         await sendMsgChain(event=event, msg=makeMsgChain(
    #             text=tenhou.getalltags(event.group.id, target=target, searchtype=searchtype)))

    '''通用功能'''

    '''随机搞怪回复'''


    @bot.on(GroupMessage)
    async def duideduide(event: GroupMessage):
        if not settings['silence']:
            if event.group.id not in silencegroup:
                if len(event.message_chain[Plain]) == 1:
                    msg = str(event.message_chain[Plain][0]).strip()

                    if msg in ['正确的', '直接的', '中肯的', '雅致的', '客观的', '整体的', '立体的', '全面的', '辩证的', '形而上学的', '雅俗共赏的', '一针见血的',
                               '直击要害的', '错误的', '间接的', '虚伪的', '庸俗的', '主观的', '平面的', '片面的', '孤立的', '辩证法的', '雅俗之分',
                               '的离题万里的',
                               '不痛不痒的']:
                        if random.random() < 0.3:
                            await bot.send(event, random.choice(
                                ['正确的', '直接的', '中肯的', '雅致的', '客观的', '整体的', '立体的', '全面的', '辩证的', '形而上学的', '雅俗共赏的',
                                 '一针见血的',
                                 '直击要害的', '错误的', '间接的', '虚伪的', '庸俗的', '主观的', '平面的', '片面的', '孤立的', '辩证法的', '雅俗之分的',
                                 '离题万里的',
                                 '不痛不痒的']))
                    # 方舟肉鸽词库
                    elif msg in ['迷茫的', '盲目的', '孤独的', '生存的', '臆想的', '谨慎的', '暴怒的', '偏执的', '敏感的']:
                        if random.random() < 0.3:
                            await bot.send(event, random.choice(
                                ['正确的', '错误的', '辩证的', '迷茫的', '盲目的', '孤独的', '生存的', '臆想的', '谨慎的', '暴怒的', '偏执的', '敏感的']))

                    elif msg in ['典', '孝', '麻', '盒', '急', '蚌', '赢', '乐', '创', '绝', '厥', '退', '急了']:
                        if random.random() < 0.3:
                            await sendMsgChain(makeMsgChain(
                                text=random.choice(['典', '孝', '麻', '盒', '急', '蚌', '赢', '乐', '创', '绝', '厥', '退', '急'])),
                                event=event)


    '''创建举牌文字'''


    @bot.on(MessageEvent)
    async def jupai(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr'''^{commandpre}{commands_map['jupai']['jupai']}''', msg.strip())
        if m:

            if len(m.group(1)) > 40:
                await bot.send(event, "最多支持做40个字的举牌哦~")
            imgoutput(event.sender.id, (m.group(1)))
            message_chain = MessageChain([
                await Image.from_local(f'./images/jupai/{event.sender.id}.png')
            ])
            await bot.send(event, message_chain)


    '''随机打断、复读、嘲讽'''


    @bot.on(GroupMessage)
    async def randominterrupt(event: GroupMessage):
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
                message_chain = MessageChain(
                    [Image(url=img_url), Plain(text=msg)])
                return await bot.send(event, message_chain)


    @bot.on(GroupMessage)
    async def diyreply(event: GroupMessage):
        if not settings['silence'] and repeatconfig['autoreply']:
            if event.group.id not in silencegroup:
                msg = "".join(map(str, event.message_chain[Plain]))
                m = re.match(fr"^{commandpre}{commands_map['reply']['jida']}", msg.strip())
                if m:
                    return await bot.send(event,
                                          f"{m.group(1)}说，他有五个鸡，我说，立直鸡，副露鸡，默听鸡，自摸鸡，放铳鸡\n{m.group(1)}还说，他有四个鸡，我说，坐东鸡，坐西鸡，坐南鸡，坐北鸡\n{m.group(1)}又说，他有三个鸡，我说，上一打鸡，这一打鸡，下一打鸡\n{m.group(1)}又说，他有两个鸡，我说，子家鸡 亲家鸡\n{m.group(1)}最后说，他有一个鸡，我说，{m.group(1)}就是鸡")
                m1 = re.match(fr"^{commandpre}{commands_map['reply']['wochao']}", msg.strip())
                if m1:
                    return await bot.send(event,
                                          f"考试中 {event.sender.member_name}想抄{m1.group(1)}的答案🥵{m1.group(1)}一直挡着说 不要抄了 不要抄了🥵当时{m1.group(1)}的眼泪都流下来了🥵可是{event.sender.member_name}还是没听{m1.group(1)}说的🥺一直在抄{m1.group(1)}🥵呜呜呜呜🥺 因为卷子是正反面 说亲自动手 趁监考老师不注意的时候把{m1.group(1)}翻到反面 翻来覆去抄{m1.group(1)}🥵抄完前面抄后面🥵🥵🥵")

                senderid = event.sender.id
                if botname == "":
                    return
                if botname in event.message_chain:
                    if senderid in black_list['user']:
                        return await bot.send(event, makeMsgChain(reply=replydata['blackuser']))
                    msg = msg.replace(f"{botname}", "", 1)
                    if settings['r18talk']:
                        if senderid in admin:
                            for k, v in replydata['r18'].items():
                                if k in msg:
                                    return await bot.send(event, makeMsgChain(reply=v, rndimg=True))
                            return await bot.send(event,
                                                  makeMsgChain(reply=replydata['mismatch']['admin'], rndimg=True))
                        else:
                            for k, v in replydata['common'].items():
                                if k in msg:
                                    return await bot.send(event, makeMsgChain(reply=v, rndimg=True))
                            return await bot.send(event,
                                                  makeMsgChain(reply=replydata['mismatch']['common'], rndimg=True))
                    else:
                        for k, v in replydata['common'].items():
                            if k in msg:
                                return await bot.send(event, makeMsgChain(reply=v, rndimg=True))
                        return await bot.send(event, makeMsgChain(reply=replydata['mismatch']['common'], rndimg=True))


    # 亲亲

    @bot.on(GroupMessage)
    async def on_kiss(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['reply']['kisskiss']}", msg.strip())
        if m:
            if At in event.message_chain:
                operator_id = event.sender.id
                target_id = event.message_chain.get_first(At).target
                if operator_id == target_id:
                    return await bot.send(event, makeMsgChain(text="请不要自交", rndimg=True))
                else:
                    await kiss(operator_id=operator_id, target_id=target_id)
                    await bot.send(event, MessageChain(
                        Image(path=f'./images/KissKiss/temp/tempKiss-{operator_id}-{target_id}.gif')))


    # 摸头

    @bot.on(GroupMessage)
    async def touchhead(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['reply']['touchhead']}", msg.strip())
        if m:
            if At in event.message_chain:
                target = event.message_chain.get_first(At).target
                await petpet(target)
                if await bot.send(event,
                                  MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif'))) == -1:
                    print('摸头发送失败')
            # else:
            #     target = m.group(2)
            #     await petpet(target)
            #     await bot.send(event, MessageChain(Image(path=f'./images/PetPet/temp/tempPetPet-{target}.gif')))


    @bot.on(MessageEvent)
    async def imgoperate(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{commands_map['imgoperation']['bw']}", msg.strip())
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


    @bot.on(GroupMessage)
    async def getremakeimg(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['remake']['remake']}", msg.strip())
        if m:

            if not cmdbuffer.updategroupcache(groupcommand(event.group.id, event.sender.id, 'remake')):
                return bot.send(event, makeMsgChain(text="打断一下,想点好的,重开也太频繁了", rndimg=True, at=event.sender.id))
            senderid = event.sender.id
            if m.group(2):
                basic_score = int(m.group(2))
            else:
                basic_score = 30
            if m.group(3):
                worlddifficulty = m.group(3)
            else:
                worlddifficulty = None
            create_remakeimg(senderid, basic_score=basic_score,
                             worlddifficulty=worlddifficulty)
            await bot.send(event, MessageChain(Image(path=f'./images/Remake/{senderid}.png')))
        return


    @bot.on(GroupMessage)
    async def sendGroupVoice(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sendvoice']['sendvoice']}", msg.strip())
        if m:
            if settings['voice']:
                if config['voicesetting']['private']:
                    if event.sender.id != master:
                        return
                text = m.group(1).strip()
                if len(text) > 40:
                    return await bot.send(event, makeMsgChain(text="文本太长啦", rndimg=True))
                voice = getbase64voice(text)
                if not voice['error']:
                    return await bot.send(event, Voice(base64=voice['file']))
                    # return await bot.send(event, await Voice.from_local(content=voice['file']))  # 有问题
                    # return await bot.send(event, await Voice.from_local(filename=f'./data/audio/{text}.{vc.codec}'))


    @bot.on(FriendMessage)
    async def sendVoiceToGroup(event: FriendMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sendvoice']['sendgroupvoice']}", msg.strip())
        if m:
            if settings['voice']:
                if config['voicesetting']['private']:
                    if event.sender.id != master:
                        return
                groupid = int(m.group(1))
                text = m.group(2).strip()
                if len(text) > 40:
                    return await bot.send(event, makeMsgChain(text="文本太长啦", rndimg=True))
                voice = getbase64voice(text)
                if not voice['error']:
                    return await bot.send_group_message(groupid, Voice(base64=voice['file']))
                    # return await bot.send(event, await Voice.from_local(content=voice['file']))  # 有问题
                    # return await bot.send(event, await Voice.from_local(filename=f'./data/audio/{text}.{vc.codec}'))


    @bot.on(MessageEvent)
    async def saveFlashImage(event: MessageEvent):
        if FlashImage in event.message_chain and settings['saveflashimg']:
            flashimg = event.message_chain.get_first(FlashImage)
            try:
                await flashimg.download(directory='./data/flashimages')
            except Exception as e:
                print(f'闪照保存发生错误: {e}')


    @bot.on(MessageEvent)
    async def getsometarots(event: MessageEvent):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sys']['tarot']}", msg.strip())
        if m:
            if m.group(1):
                num = int(m.group(1))
                if 0 < num < 10:
                    cards = tarotcards.drawcards(count=num, userid=event.sender.id)
                    msgC = []
                    for card in cards:
                        fmn = ForwardMessageNode(
                            sender_id=event.sender.id,
                            sender_name=event.sender.get_name(),
                            message_chain=MessageChain(
                                [Image(base64=card.imgcontent)])
                        )
                        # fmn = ForwardMessageNode.create(event.sender,MessageChain([Image(base64=card.imgcontent)]))
                        msgC.append(fmn)
                        # msgC.append(Image(base64=card.imgcontent))
                    # ForwardMessageNode(event.sender,MessageChain(msgC))
                    return await bot.send(event, Forward(node_list=msgC))
                else:
                    return await sendMsgChain(event=event, msg=makeMsgChain(text='每次只能抽1-9张塔罗牌哦', rndimg=True))
            else:
                card = tarotcards.drawcards(userid=event.sender.id)[0]
                return await bot.send(event, Image(base64=card.imgcontent))


    # 获取塔罗牌抽卡记录

    @bot.on(GroupMessage)
    async def getmytarots(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sys']['getmytarot']}", msg.strip())
        if m:
            msg = tarotcards.getmydrawcardsinfo(event.sender.id)
            return await bot.send(event, makeMsgChain(text=msg))


    # 戳一戳 出发摸头

    @bot.on(NudgeEvent)
    async def Nudgepetpet(event: NudgeEvent):

        sender = event.from_id

        if sender == bot.qq:
            return
        if (not settings['silence']) or settings['nudgereply']:
            if event.subject.kind == 'Group':
                if not (event.subject.id in silencegroup or event.subject.id in nudgeconfig['disnudgegroup']):
                    target = event.target
                    if target == bot.qq:
                        if sender in admin:
                            await bot.send_group_message(event.subject.id,
                                                         MessageChain(
                                                             [Plain(random.choice(replydata['nudgedata']['admin']))]))
                            await petpet(target)
                            await bot.send_group_message(event.subject.id,
                                                         MessageChain(
                                                             await Image.from_local(
                                                                 filename=f'./images/PetPet/temp/tempPetPet-{target}.gif')))
                        else:
                            if random.random() < nudgeconfig['sendnudgechance']:
                                if random.random() < nudgeconfig['supersendnudgechance']:
                                    await bot.send_group_message(event.subject.id,
                                                                 makeMsgChain(
                                                                     reply=replydata['nudgedata']['supernudgereply'],
                                                                     rndimg=True))
                                    for i in range(nudgeconfig['supernudgequantity']):
                                        await bot.send_nudge(subject=event.subject.id, target=sender, kind='Group')
                                    return
                                else:
                                    await bot.send_nudge(subject=event.subject.id, target=sender, kind='Group')
                                    return await bot.send_group_message(event.subject.id,
                                                                        makeMsgChain(
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


    # 定时任务
    # 设定为每分钟执行一次

    @scheduler.scheduled_job(CronTrigger(hour='*', minute=f'*'))
    async def allscheduledtask():
        # 时分秒
        minute_now = datetime.datetime.now().minute
        hour_now = datetime.datetime.now().hour
        second_now = datetime.datetime.now().second
        if minute_now == 0:
            if hour_now == 0:
                cmdbuffer.clearcache()
                cleaner.do_clean()  # 每天0点清理所有pil生成的图片
                # global rootLogger, qqlogger
                # rootLogger = create_logger(config['loglevel'])
                # qqlogger = getQQlogger()

            if 7 < hour_now < 23:
                for groupid in alarmclockgroup:
                    if groupid != 0 and type(groupid) == int:
                        await bot.send_group_message(groupid,
                                                     makeMsgChain(text=f"准点报时: {datetime.datetime.now().hour}:00",
                                                                  rndimg=True))
                        if hour_now == 22:
                            await bot.send_group_message(groupid, makeMsgChain(text="晚上10点了，大家可以休息了", rndimg=True))
        if minute_now % config["searchfrequency"] == 0:
            if settings['autogetpaipu']:
                print(f"开始查询,当前时间{hour_now}:{minute_now}:{second_now}")
                try:
                    await asyth_all()
                    await asyqh_autopaipu()
                except sqlite3.OperationalError as e:
                    logging.warning("自动查询失败,可能是数据库不存在或者表不存在,牌谱查询将关闭")
                    logging.warning(f'{e}')
                    settings['autogetpaipu'] = False
                except websockets.exceptions.ConnectionClosedError as e:
                    logging.error(f'websockets发生错误{e}')
                    logging.exception(e)
                    exit(0)
                except Exception as e:
                    logging.error(f'发生未知错误{e}')
                    logging.exception(e)
                print(
                    f"查询结束,当前时间{hour_now}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}")


    bot.run(port=17580)
