# Majsoul-QQBot
一个基于YiriMirai的QQ机器人，有查询雀魂玩家信息、播报牌谱
、模拟十连、入群欢迎 和 举牌等功能。

后续会添加更多的功能来让机器人更加完善。

# 如何实现
数据来自[雀魂牌谱屋](https://amae-koromo.sapk.ch/)，通过定时爬取来获取牌谱。


# 如何部署
需要先安装 mirai 和 mirai-api-http，在mirai-api-http的配置文件中修改adapter和adapterSettings，再下载本程序，在config.yml中配置好相关参数后就可以直接使用命令行启动。
可以参考 YiriMirai 的[官方文档](https://yiri-mirai.wybxc.cc/docs/quickstart)的快速部署。

本程序 `WebSocketAdapter` 的端口号为 `17280`，运行在端口`17580`上 ~~不会占用你可能会使用的Tomcat的8080端口~~

# 配置文件
中文如果出现乱码，可以使用 VSCode “通过编码重新打开” ，选择编码为GBK。
 ```
admin: # 管理员QQ
- 0
alarmclockgroup: # 为群聊添加每天早安和准点报时
- 0
blacklist: # 黑名单(目前没做)
- 0
mutegrouplist: # 屏蔽某群的消息(目前没做)
- 0
settings: # 设置
  autogetpaipu: true  # 自动抓取牌谱并广播
  autowelcome: true # 自动欢迎新人入群
welcomeinfo: 
# 欢迎消息,新人入群会从下面随机选择一条发送。 
# %ps% 用于指代新入群的用户名字, %gn% 用于指代加入的群的群名字
- 欢迎 %ps% 加入群聊 %gn%
whitelist: # 白名单(目前只有不复读白名单用户的功能)
- 0

 ```

 # 存在的问题
 1. 查询玩家信息的时候仍然会卡死，可能是由于超时。
 2. config.yml编辑后乱码 ~~（大多数时候是将 UTF-8 编码保存为 GBK 或者反过来）~~

# 开源协议
由于 [mirai](https://github.com/mamoe/mirai) 、 mirai-api-http 、 [YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) 均采用了 AGPL-3.0 开源协议，本项目同样采用 AGPL-3.0 协议。

请注意，AGPL-3.0 是传染性协议。如果你的项目引用了 YiriMirai，请在发布时公开源代码，并同样采用 AGPL-3.0 协议。