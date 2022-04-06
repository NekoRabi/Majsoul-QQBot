# yaml.scanner.ScannerError:
解决方法：yaml文件的格式不对，请检查 冒号 (:) 和 横线 (-) 后面是否有空格，并检查缩进

# ERORAs of 3.10， the *loop* parameter was removed from Lock() since it is no longer necessaryTraceback (most recent call last) :
解决方法：参数 loop 已从 python 3.10 中移除，请降级安装python 3.8 或 3.9 ，或者参考 [官方办法](https://yiri-mirai.vercel.app/docs/faq#as-of-310-the-loop-parameter-was-removed-from-lock-since-it-is-no-longer-necessary)

# 启动后秒退
如果看到这样的问题，请安装 uvicorn 或 hypercorn
```
2021-08-07 09:06:46 - WARNING  未找到可用的 ASGI 服务，反向 WebSocket 和 WebHook 上报将不可用。
仅 HTTP 轮询与正向 WebSocket 可用。
建议安装 ASGI 服务器，如 `uvicorn` 或 `hypercorn`。
在命令行键入：
    pip install uvicorn
或者
    pip install hypercorn
2021-08-07 09:06:46 - INFO     [HTTP] 成功登录到账号12345678。
2021-08-07 09:06:46 - INFO     [WebHook] 成功登录到账号12345678。
2021-08-07 09:06:47 - INFO     [WebHook] 从账号12345678退出。
2021-08-07 09:06:47 - INFO     [HTTP] 从账号12345678退出。
```
解决方法
```
pip install uvicorn 
或
pip install hypercorn
```
#  文件打开错误，尝试生成初始文件中...

请检查config.yml的数据是否齐全，格式是否正确 **(冒号和横线后面必须有空格)**


# mirai.exceptions.ApiError: ERROR 51发送消息目标不存在，或指定对象不存在。

使用 `bot.send_group_message(groupid,MessageChain)`时，需要指定发送的群组id，请检查groupid是否有误，机器人是否加入了这个群聊。

一般多出现于发送准点报时功能，如果不需要该功能，请在config中将 `alarmclockgroup` 设置为 0
```
alarmclockgroup: # 设置闹钟群聊
- 0
```

# sqlite3.OperationalError: no such table:xxx
数据库错误:缺少表xxx

请用`sqlite`打开相应插件的数据库文件，检查是否有这张表

# ERROR  [WebSocket] WebSocket通道意外关闭。code: 1006，reason:

websocket通道异常关闭，当前版本来说，一般是由异步爬虫引起的，可能一天会掉线一次，暂不清楚如何解决。