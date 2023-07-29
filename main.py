"""
:Author:  NekoRabi
:Update Time:  2022/9/18 2:57
:Describe: Bot入口函数
:Version: v0.6.5
"""
import nest_asyncio
from mirai import MessageEvent
from mirai.models import FlashImage, Source
from core import *
from plugin import *
from utils import *
from utils.bufferpool import cmdbuffer

nest_asyncio.apply()

if __name__ == '__main__':

    config = load_config()
    if config.get('setting',{}).get('general_help',True):
        create_helpimg()
    settings = config['settings']
    botname = config['botconfig']['botname']

    print(f"机器人{botname}启动中\tQQ : {bot.qq}")


    # 聊天记录存储

    @bot.on(MessageEvent)
    def add_event_log(event: MessageEvent):
        if isinstance(event, GroupMessage):
            # infodict = dict(type=event.type,senderid=event.sender.id,sendername=event.sender.get_name(),
            # groupname=event.group.name,groupid=event.group.id,message=event.message_chain)
            # qqlogger.info(infodict)
            msgchain = []
            for item in event.message_chain:
                if type(item) != Source:
                    msgchain.append(item)
            _info = {'groupid': event.group.id, 'groupname': event.group.name, 'membername': event.sender.member_name,
                  'message': msgchain}
            root_logger.info(_info)
        elif isinstance(event, FriendMessage):
            msgchain = []
            for item in event.message_chain:
                if type(item) != Source:
                    msgchain.append(item)
            _info = {'friendid': event.sender.id, 'friendname': event.sender.nickname, 'message': msgchain}
            root_logger.info(_info)


    # @bot.on(MessageEvent)
    # async def save_flashimage(event: MessageEvent):
    #     if type(event) in [GroupMessage, FriendMessage]:
    #         if FlashImage in event.message_chain and settings['saveflashimg']:
    #             flashimg = event.message_chain.get_first(FlashImage)
    #             try:
    #                 await flashimg.download(directory='./data/flashimages')
    #             except Exception as _e:
    #                 print(f'闪照保存发生错误: {_e}')


    scheduler.add_job(cmdbuffer.clearcache, 'cron', hour='0')
    scheduler.add_job(cleaner.do_clean, 'cron', hour='0')

    bot.run(port=17580)
