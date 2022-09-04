"""
:Author:  NekoRabi
:Create:  2022/9/5 2:13
:Update: /
:Describe: 自定义插件的模板
:Version: 0.0.1
"""
import re

from mirai import GroupMessage, Plain

from core import bot, config, bot_cfg


@bot.on(GroupMessage)  # 当群聊事件发生时
async def helloworld(event: GroupMessage):
    """
    定义一个方法
    @param event: 群聊事件
    @return:
    """
    msg = "".join(map(str, event.message_chain[Plain])) # 获取消息的文本内容
    m = re.match(fr"^你好$", msg.strip()) # 用正则进行匹配指令
    if m:
        # 如果匹配指令,执行方法
        # do()

        # 最后让机器人发信息，给出反馈,可以用utils.MessageChainBuilder包的 messagechain_builder() 方法来快速构造一个消息链
        await bot.send(event, f'Hello World! This is {bot_cfg.get("nickname")}')
