

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

# AttributeError: 'NoneType’object has no attribute 'call_soon_threadsafeTraceback (most recent call last) :
可能是由以下代码引起的，可以在 main.py 中将这段删掉

**大概率是由 _task.cancel() 引起的**
```
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
        global _task
        if _task:
            _task.cancel()
```
