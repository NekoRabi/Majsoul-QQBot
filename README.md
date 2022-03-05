# 当前正在快速写bot，短期内各种config 和 py文件可能都会发送巨大的变化

# 项目缓慢重构中，逻辑非常乱 
~~当然原来也很乱~~

# Majsoul-QQBot
一个基于YiriMirai的QQ机器人，有查询雀魂玩家信息、播报牌谱
、模拟十连、入群欢迎 和 制作图片等功能。

后续会添加更多的功能来让机器人更加完善。

# 如何实现
数据来自[雀魂牌谱屋](https://amae-koromo.sapk.ch/)，通过定时爬取来获取牌谱。


# 如何部署
需要先安装 mirai 和 mirai-api-http，在mirai-api-http的配置文件中修改adapter和adapterSettings，再下载本程序，在config.yml中配置好相关参数后就可以直接使用命令行启动。
可以参考 YiriMirai 的[官方文档](https://yiri-mirai.wybxc.cc/docs/quickstart)的快速部署。

本程序 `WebSocketAdapter` 的端口号为 `17280` 

# 配置文件
中文如果出现乱码，可以使用 VSCode “通过编码重新打开” ，选择编码为GBK。
### config.yml
 ```
adapter: # Mirai-Http-adapter参数
  host: localhost
  port: 17280
  verify_key: NekoRabi
admin: # 管理员QQ
- 0
alarmclockgroup: # 为群聊添加每天早安和准点报时
- 0
blacklist: # 黑名单
- 0
botname: '' #与机器人对话时的机器人名字
commandpre: '' #指令前缀
botconfig: # 机器人配置
  botname: "" # 机器人的称呼，用来和机器人聊天
  host: localhost 
  port: 17280
  qq: 123456
  verify_key: NekoRabi
searchfrequency: 6 # 雀魂牌谱查询频率(单位: 分钟)，不要太快,最好为60的因数，网络请求很耗时间，在查询的过程中机器人不会对外响应，尤其是数据库用户很多的时候
                   # 建议为 5-6
mutegrouplist: # 屏蔽某群的消息(目前没做)
- 0
settings: # 设置
  autogetpaipu: true  # 自动抓取牌谱并广播,默认开启
  autowelcome: true # 自动欢迎新人入群,默认开启
  r18talk: true

welcomeinfo: 
# 欢迎消息,新人入群会从下面随机选择一条发送。 
# %ps% 用于指代新入群的用户名字, %gn% 用于指代加入的群的群名字
- 欢迎 %ps% 加入群聊 %gn%
whitelist: # 白名单(目前只有不复读白名单用户的功能)
- 0

 ```

### reply.json
```
{
  <!-- 都是最简单的 key:[value0,value1...]  
  前面是与机器人互动的关键词 string ，后面是回复消息的 list -->
  "贴": [
      "贴什么贴.....只......只能......一下哦！",
      "贴...贴贴（靠近）",
      "蹭蹭…你以为咱会这么说吗！baka死宅快到一边去啦！",
      "你把脸凑这么近，咱会害羞的啦Σ>―(〃°ω°〃)♡→",
      "退远",
      "不可以贴"
  ]
}
```

### 雀魂十连的 drawcards.yml 

```
lottery:    # 奖池
  decoration:  # 装饰品类
    item: # 物品
    - index: 0 # 编号
      name: 24K金棒 # 物品名称
      rare: 3  #稀有度
      type: decoration # 物品类型
      url: ./Images/decoration/24K金棒.jpg  # 物品图片链接
    - index: 1
      name: 一触即发
      rare: 3
      type: decoration
      url: ./Images/decoration/一触即发.jpg
    - index: 2
  gift:  # 礼物类
    item:
    - index: 0
      name: 手工曲奇
      rare: 0 
      type: gift
      url: ./Images/gift/00-手工曲奇.jpg
    - index: 1
      name: 蓝罐曲奇
      rare: 1
      type: gift
      url: ./Images/gift/01-蓝罐曲奇.jpg
    - index: 2
      name: 香喷喷曲奇
      rare: 2 
      type: gift
      url: ./Images/gift/02-香喷喷曲奇.jpg
  person:
    item:
    - index: 0
      name: 七海礼奈
      rare: 4
      type: person
      url: ./Images/person/七海礼奈.png
    - index: 1
      name: 三上千织
      rare: 4
      type: person
      url: ./Images/person/三上千织.png

up: # up的物品池，如果十连参数为 限时，up列表的装扮和人物出率将提高
    # 直接填物品名字
  decoration:
  - 和牌-安可
  - 立直-开场曲
  - 立直棒-应援棒
  person:
  - 八木唯
  - 北见纱和子
```


 # 功能

 - 雀魂相关功能，如模拟抽卡，查询玩家信息，定时播报玩家最近战绩
 - 入群欢迎
- 摸头、举牌等图片制作功能
- 自定义回复

 # 存在的问题
 1. 查询玩家信息的时候仍然会卡死，可能是由于超时。
 2. config.yml编辑后乱码。 ~~（基本候是将 UTF-8 编码保存为 GBK 或者反过来）~~
 解决办法: 将config.yml用GBK编码打开并保存 

 # 开发计划
  [√] 将十连的图片合并为一张

  [ ] 增加何切

  [ ] 增加对天凤的支持

  [√] 指令增加英文缩写触发

  [ ] 更多更多的功能

  [?]将所有功能都写进配置文件，提供高度自定义

  [ ]打包成exe

# 联系方式
QQ:1215791340 验证消息： 可爱的拉克丝

有需求、bug、问题欢迎提的

# 开源协议
由于 [mirai](https://github.com/mamoe/mirai) 、 mirai-api-http 、 [YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) 均采用了 AGPL-3.0 开源协议，本项目同样采用 AGPL-3.0 协议。

请注意，AGPL-3.0 是传染性协议。如果你的项目引用了或改造了我的项目，请在发布时公开源代码，并同样采用 AGPL-3.0 协议。

# 参考项目
[YiriMirai](https://github.com/YiriMiraiProject/YiriMirai)

[Yuzi_project](https://github.com/MEYUYU/yuzi-project)

[Mirai](https://github.com/mamoe/mirai)

[Saya_plugins_collection](https://github.com/SAGIRI-kawaii/saya_plugins_collection)

[AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus)
