"""
:Author:  NekoRabi
:Create:  2022/9/18 2:49
:Update: /
:Describe: 自定义插件的模板
:Version: 0.0.2
"""
import re

# 用正则来匹配指令，正则表达式模块( re )当然是必须需导入的

from mirai import GroupMessage, Plain, FriendMessage

# 一般来说,Plain 是必选 , GroupMessage 和 FriendMessage 依据你的插件触发情况是群聊还是私聊再选择导入

from core import bot, config, bot_cfg


# bot 是必须导入的, config 和 bot_cfg 是可选
# config 是系统配置文件，有 指令前缀、黑白名单 等等
# bot_cfg 是机器人的配置，比如 QQ号、昵称 等等数据

# 还可以import其他的模块，比如 工具类,sqlite3,asyncio,time,math 等等


async def asy_hello():
    """
    这是一个异步方法,当你进行异步请求时，定义方法需要加上 async , 在使用时需要加上 await
    Returns:

    """
    # 网络请求都是异步的，大多数方法都不需要写成异步

    return "执行了异步方法 HELLOWORLD!"


def common_hello():
    """
    这是普通的方法
    Returns:

    """
    return "hello world"


@bot.on(GroupMessage)  # 当群聊事件发生时
async def helloworld(event: GroupMessage):
    """
    定义一个方法
    @param event: 群聊事件
    @return:
    """
    msg = "".join(map(str, event.message_chain[Plain]))  # 获取消息的文本内容
    m = re.match(fr"^你好$", msg.strip())  # 用正则进行匹配指令
    if m:
        # 如果匹配指令,执行方法
        # do()

        # 调用异步方法
        # msg = await asy_hello()
        # 普通方法调用
        # msg = common_hello()

        # from utils.MessageChainBuilder import messagechain_builder
        # 最后让机器人发信息，给出反馈,可以用utils.MessageChainBuilder包的 messagechain_builder() 方法来快速构造一个消息链

        await bot.send(event, f'114514191810 ! This is {bot_cfg.get("nickname")}')


@bot.on(FriendMessage)  # 当私聊事件发生时
async def helloworld(event: FriendMessage):
    """
    定义一个方法
    @param event: 私聊事件
    @return:
    """
    msg = "".join(map(str, event.message_chain[Plain]))  # 获取消息的文本内容
    m = re.match(fr"^你好$", msg.strip())  # 用正则进行匹配指令
    if m:
        # 如果匹配指令,执行方法
        # do()

        # 调用异步方法
        # msg = await asy_hello()
        # 普通方法调用
        # msg = common_hello()

        from utils.MessageChainBuilder import messagechain_builder
        # 最后让机器人发信息，给出反馈,可以用utils.MessageChainBuilder包的 messagechain_builder(text=msg) 方法来快速构造一个消息链

        await bot.send(event, f'私聊成功! This is {bot_cfg.get("nickname")}')
