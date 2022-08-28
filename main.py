import datetime
import re

import nest_asyncio
from apscheduler.triggers.cron import CronTrigger
from mirai import MessageEvent, Voice, FriendMessage, Plain, GroupMessage
from mirai.models import FlashImage

from core import *
from plugin import *
from utils.MessageChainBuilder import messagechain_builder
from utils.bufferpool import cmdbuffer
from utils.file_cleaner import cleaner
from utils.text_to_voice import VoiceCreater
from utils import *

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


    # 定时任务
    # 设定为每分钟执行一次

    @scheduler.scheduled_job(CronTrigger(hour='8-22'))
    async def allscheduledtask():
        # 时分秒
        minute_now = datetime.datetime.now().minute
        hour_now = datetime.datetime.now().hour
        second_now = datetime.datetime.now().second
        for groupid in alarmclockgroup:
            if groupid != 0 and type(groupid) == int:
                await bot.send_group_message(groupid,
                                             messagechain_builder(
                                                 text=f"准点报时: {datetime.datetime.now().hour}:00",
                                                 rndimg=True))
                if hour_now == 22:
                    await bot.send_group_message(groupid,
                                                 messagechain_builder(text="晚上10点了，大家可以休息了", rndimg=True))


    scheduler.add_job(cmdbuffer.clearcache, 'cron', hour='0')
    scheduler.add_job(cleaner.do_clean, 'cron', hour='0')
    bot.run(port=17580)
