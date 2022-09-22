***代码都在 [plugin/Template 包](../plugin/Template)中***

# 一、先引入需要用的包和模块
```python


import re
from core import bot, config, bot_cfg
from mirai import GroupMessage, Plain, FriendMessage

# 用正则来匹配指令，正则表达式模块( re )当然是必须需导入的
# 一般来说,Plain 是必选 , GroupMessage 和 FriendMessage 依据你的插件触发情况是群聊还是私聊再选择导入
# bot 是必须导入的, config 和 bot_cfg 是可选
# config 是系统配置文件，有 指令前缀、黑白名单 等等
# bot_cfg 是机器人的配置，比如 QQ号、昵称 等等数据

# 还可以import其他的模块，比如 工具类,sqlite3,asyncio,time,math 等等
```

# 二、创建一个方法
```python
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

def readfile(path):
    """
    稍微复杂一些的方法 
    目的是读取文件
    Args:
        path: 文件路径

    Returns: 文件读取结果

    """

    # 引入我封装好的方法 - 读取文件
    from utils.cfg_loader import read_file
    data = read_file(path)
    print(data)
    return data

```
# 三、创建bot方法，执行事务

```python

import re
from core import bot, bot_cfg
from mirai import GroupMessage, Plain, FriendMessage

@bot.on(GroupMessage)  # 当群聊事件发生时
async def helloworld(event: GroupMessage):
    """
    定义一个群聊方法
    @param event: 群聊事件
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
    定义一个私聊方法
    @param event: 私聊事件
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

```

# 四、编写__init__.py文件

在目录的文件下, 创建一个名为 `__init__.py`的文件
再用编辑器打开`__init__.py` (可用 记事本 / Notepad / *推荐*VScode)
```python
# 当你的插件都编写好后
# 把你写的插件文件，按照 plugin.包名.文件名 的形式引入
# 将下面的 'Template' 重命名为你文件夹的名字
# 将文件夹中除了 '__init__.py' 以外全部的python文件全部导入

# from plugin.Template.file_init import *
# from plugin.Template.helloworld import *
```

# 五、将你写好的 ___文件夹___  移动到机器人的plugin文件中

# 六、运行机器人, 进行测试

# 其他
<font size=5>
<ul>
<li>可以编写一个`file_init.py`文件，用来初始化所有配置</li>
<li>确定没有问题了,可以上传至群文件共享</li>
</ul>
</font>