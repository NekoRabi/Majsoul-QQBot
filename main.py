import datetime
import logging
import re

import nest_asyncio
import websockets.exceptions
from apscheduler.triggers.cron import CronTrigger
from mirai import MessageEvent, Voice, FriendMessage, Plain, GroupMessage
from mirai.models import FlashImage

from core import *
from plugin import *
from utils.MessageChainBuilder import messagechain_builder
from utils.bufferpool import cmdbuffer
from utils.file_cleaner import cleaner
from utils.text_to_voice import VoiceCreater

nest_asyncio.apply()

if __name__ == '__main__':

    config = load_config()
    replydata = load_replydata()
    create_helpimg()
    qqlogger = getQQlogger()
    rootLogger = create_logger(config['loglevel'])
    admin: list = config['admin']
    master = config['master']
    settings = config['settings']
    botname = config['botconfig']['botname']
    alarmclockgroup = config['alarmclockgroup']
    vc = None

    if settings['voice']:
        vc = VoiceCreater(setting=config['voicesetting'])

    if master not in admin:
        admin.append(master)
    print(f"机器人{botname}启动中\tQQ : {bot.qq}")

    def getbase64voice(text):
        voice = dict(error=False, file=None, errmsg=None)
        if vc:
            voice['file'] = vc.getbase64voice(text=text)
        else:
            voice['error'] = True
        return voice


    # 聊天记录存储

    @bot.on(MessageEvent)
    def add_event_log(event: MessageEvent):
        if event.type == 'GroupMessage':
            # infodict = dict(type=event.type,senderid=event.sender.id,sendername=event.sender.get_name(),
            # groupname=event.group.name,groupid=event.group.id,message=event.message_chain)
            # qqlogger.info(infodict)
            qqlogger.info(event)
        else:
            qqlogger.info(event)





    '''通用功能'''

    @bot.on(GroupMessage)
    async def send_group_voice(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{commands_map['sendvoice']['sendvoice']}", msg.strip())
        if m:
            if settings['voice']:
                if config['voicesetting']['private']:
                    if event.sender.id != master:
                        return
                text = m.group(1).strip()
                if len(text) > 40:
                    return await bot.send(event, messagechain_builder(text="文本太长啦", rndimg=True))
                voice = getbase64voice(text)
                if not voice['error']:
                    return await bot.send(event, Voice(base64=voice['file']))
                    # return await bot.send(event, await Voice.from_local(content=voice['file']))  # 有问题
                    # return await bot.send(event, await Voice.from_local(filename=f'./data/audio/{text}.{vc.codec}'))


    @bot.on(FriendMessage)
    async def send_voice_to_group(event: FriendMessage):
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
                    return await bot.send(event, messagechain_builder(text="文本太长啦", rndimg=True))
                voice = getbase64voice(text)
                if not voice['error']:
                    return await bot.send_group_message(groupid, Voice(base64=voice['file']))
                    # return await bot.send(event, await Voice.from_local(content=voice['file']))  # 有问题
                    # return await bot.send(event, await Voice.from_local(filename=f'./data/audio/{text}.{vc.codec}'))


    @bot.on(MessageEvent)
    async def save_flashimage(event: MessageEvent):
        if event is GroupMessage or FriendMessage:
            if FlashImage in event.message_chain and settings['saveflashimg']:
                flashimg = event.message_chain.get_first(FlashImage)
                try:
                    await flashimg.download(directory='./data/flashimages')
                except Exception as _e:
                    print(f'闪照保存发生错误: {_e}')


    # 群龙王
    # @bot.on(GroupEvent)
    # async def dradonchange(event: MemberHonorChangeEvent):
    #     if event.member.id == bot.qq:
    #         if event.honor == 'TALKACTIVE':
    #             if event.action == 'lose':
    #                 await bot.send(event, "呜呜，我的龙王被抢走惹~")
    #             else:
    #                 await bot.send(event, "我是水群冠军！")

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
                                                     messagechain_builder(
                                                         text=f"准点报时: {datetime.datetime.now().hour}:00",
                                                         rndimg=True))
                        if hour_now == 22:
                            await bot.send_group_message(groupid,
                                                         messagechain_builder(text="晚上10点了，大家可以休息了", rndimg=True))
        if minute_now % config["searchfrequency"] == 0:
            if settings['autogetpaipu']:
                print(f"开始查询,当前时间{hour_now}:{minute_now}:{second_now}")
                try:
                    await asyth_all()
                    await asyqh_autopaipu()
                except websockets.exceptions.ConnectionClosedError as _e:
                    logging.error(f'websockets发生错误{_e}')
                    logging.exception(_e)
                    exit(0)
                except Exception as _e:
                    logging.error(f'发生未知错误{_e}')
                    logging.exception(_e)
                print(
                    f"查询结束,当前时间{hour_now}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}")


    bot.run(port=17580)
