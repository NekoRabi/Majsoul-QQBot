# Majsoul-QQBot
一个基于YiriMirai的QQ机器人，主要有雀魂和天凤的相关功能(如查询、十连、监控等等)，还有一些娱乐性的功能，比如入群欢迎，制作/发送图片，随机复读等等

# [指令帮助](./docs/command_help.md)

# 效果展示

## 十连模拟抽卡

![雀魂十连](./other/效果展示/雀魂十连.png)

## 查一个玩家的数据

![雀魂玩家详情](./other/效果展示/雀魂玩家详情.png)

## 自动播报对局信息

![自动抓取牌谱](./other/效果展示/自动抓取牌谱.png)


## 查询玩家的最近对局情况

![最近对局](./other/效果展示/最近对局.png)

## 对局开始报幕

![thstartmatch](./other/效果展示/thstartmatch.png)

## 对局结算播报

![thbordercastmatch](./other/效果展示/thbordercastmatch.png)

# 如何实现

雀魂数据来自[雀魂牌谱屋](https://amae-koromo.sapk.ch/)，通过定时爬取来获取牌谱。

以后可能会改成从雀魂直接获取数据 ( 等我会使用 websocket )

天凤数据来自角田提供的数据接口，自行存储数据


# 常见错误

[查看帮助](./docs/faq.md)

# 如何使用

需要先安装 mirai 和 mirai-api-http，在mirai-api-http的配置文件中修改adapter和adapterSettings，再下载本程序，在config.yml中配置好相关参数后就可以直接使用命令行启动。

如果Mirai安装了`chat-command`，建议在Mirai控制台界面中输入 `/perm permit u* console:command.help`，来禁用Mirai的帮助输出。

可以参考 YiriMirai 的[官方文档](https://yiri-mirai.wybxc.cc/docs/quickstart)的快速部署。

可以使用 ``` pip install -r requirements.txt``` 来快速安装所需依赖。

我提供了自己的 [Mirai](./other/自用mirai/mcl1.0.6.zip) 和 [Mirai-Api-Http](./other/mirai-api-http/setting.yml) 配置，可以直接进行复制和替换。

本程序 `WebSocketAdapter` 的端口号为 `17280`。 


配置文件填写好后就可以启动了。双击 `start.bat` 或者打开命令行(cmd)，执行`python main.py`

# 环境

我自己环境是 Python 3.9  和 Java 17.

**建议使用 Python 3.9 和 Java 17**

已知Python 3.10 可能有问题跑不起来，如已安装并报错，请降级安装python 3.8-9 *以后会去解决3.10的问题*

# 关于风控

风控相当于把这台设备禁言了，能够收到消息，后台显示发出消息了，但是并没发出去

如果是初次使用，风控几乎是必然的。机器人挂着放一两天就好了。

# 配置文件

### config.yml
 ``` 注意, '冒号' (:) 后必须有空格 ```
 ```
### 请注意 ， 冒号(:)和横线(-)  后面必须要有 '空格'

adapter: # Mirai-api-http
  host: localhost
  port: 17280
  verify_key: NekoRabi

botconfig:
  botname: '' # 机器人名字
  qq: 123456  # 机器人QQ

admin: # 以下都是管理员
  - 1215791340

alarmclockgroup: # 设置闹钟群聊
  - 0

blacklist: # 黑名单
  - 0

mutegrouplist:
  - 0

commandpre: ''  # 指令前缀

master: 0  # 机器人主人

searchfrequency: 6 # 查询频率，建议为 6

replyimgpath : fox # 表情包选择,请将表情包方放在文件夹'data/reply/img/'下以

loglevel: INFO # 日志等级,功能暂时关闭

# "戳一戳"配置文件
nudgeconfig:
  # 在某群禁用 摸头事件
  disnudgegroup:
    - 0
  sendnudgechance: 1  # 被戳时 以 "戳一戳" 还击的概率
  supersendnudgechance: 0.2 # 还击的"戳一戳"中，触发超级还击的概率
  supernudgequantity: 10 # 单次超级还击的发送 "戳一戳" 的次数

# 在某群关闭自动回复
norepeatgroup:
  - 0

silencegroup:
  - 0     # 设置单群沉默

welcomeinfo:  # 新人入群欢迎词，%ps%为新人名字，%gn%为群聊名字
  - 欢迎%ps%加入%gn%

whitelist:
  - 0   # 白名单

# 色图群聊
setugroups:
  - 0

settings: # 功能开关
  autogetpaipu: true  # 自动获取雀魂牌谱
  autowelcome: true   # 自动欢迎新人
  nudgereply: true    # 是否启用摸头事件
  r18talk: true       # 开启管理员词库
  setu: false         # 色图
  silence: false      # 全局沉默,降低发言频率
  norepeat: false     # 全局自动回复
  help: true          # 是否显示帮助
  voice: false        # 语音功能
  saveflashimg: false # 保存闪照

repeatconfig:         # 回复、打断相关，要求值从上到下排序为从大到小，值为 百分数
  repeatQ: 20         # 复读问号 的概率
  repeatmsg: 1        # 复读的概率
  interruptQ: 0.5     # 用 ? 打断发言的概率
  interruptQQ: 0.1    # 用 ? 或多个??打断发言的概率

# 雀魂指令控制
qhsettings: # 是否启用
  qhpt: true
  qhinfo: true
  qhsl: true
  qhyb: true
  qhpaipu: true
  disptgroup: # 在某群禁用 qhpt
    - 0
  disinfogroup:
    - 0
  disslgroup:
    - 0
  disybgroup:
    - 0
  disautoquerygroup:
    - 0
  dispaipugroup:
    - 0


#语音设置
voicesetting:
  # 腾讯云文本转语音系统，请在使用前仔细看使用手册
  # https://cloud.tencent.com/document/product/1073/37995
  # 密钥可前往https://console.cloud.tencent.com/cam/capi网站进行获取
  volume: 1       # 音量或是音高
  speed: 0.9      # 语速
  voicetype: 1002 # 音色或是音质
  private: true   # 因为该功能可能需要机器人主人承担一定的费用，因此你可以设置该功能是否为私人使用
                  # 即 设置private 为 true，则只有你可以让机器人说话
  secretId: ''
  secretKey: ''
  codec: 'mp3'    # 音频格式,为 'mp3'或'wav'



 ```
## 回复文本相关
### 以 commonreply.json 为例
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

### 雀魂十连的配置 drawcards.yml 
#### 我会不定期更新配置和图片资源

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

up: # up的物品池，如果十连参数为 限时，up列表的装扮和人物出率将提高(与雀魂一致)
    # 直接填名字
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
 - 天凤对局播报，段位查询
 - 入群欢迎
 - 摸头、互亲、举牌、色图、占卜等图片相关功能
 - 强交互性，提供自定义回复、图片回复和语音回复
 - 支持自定义指令，可以自定义自己喜欢的触发方式
 - 以后会有更多……

 # 存在的问题
 1. config.yml编辑后乱码。 ~~（基本候是将 UTF-8 编码保存为 GBK 或者反过来）~~
 解决办法: 将config.yml重新编码 ( 现已全部都使用 utf-8 编码 ) 
 2. ~~网络请求超时(网络不好)~~
 3. 天凤关注订阅时，新加入的玩家 ( 并且未在数据库注册过 ) 如果在短时间内 ( 2小时 ) 狂打,会出现输出多个播报对局的情况

 # 开发计划

  [ ] 数据库重新设计 ( 快完成了!! )

  [ ] 增加何切支持

  [?] 将所有功能都写进配置文件，提供高度自定义

  [ ] 打包成exe,或者一键启动与更新

  [ ] 做一份完整的说明书

# 其他
语音模块是使用的腾讯云的api，是收费的，默认关闭，有想法可以打开玩玩，约 0.02 或 0.03 元  

[腾讯云语音模块地址](https://cloud.tencent.com/document/product/1073/37995)

# 联系方式
QQ:1215791340 验证消息： 可爱的拉克丝

群聊: 586468489

欢迎提交 需求、BUG、问题，也可以找我询问项目相关的问题

# 开源协议
由于 [mirai](https://github.com/mamoe/mirai) 、 mirai-api-http 、 [YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) 均采用了 AGPL-3.0 开源协议，本项目同样采用 AGPL-3.0 协议。

请注意，AGPL-3.0 是传染性协议。如果你的项目引用了或改造了我的项目，请在发布时公开源代码，并同样采用 AGPL-3.0 协议。

# 项目支持
[Mirai](https://github.com/mamoe/mirai) : 提供 QQ Android 协议支持的高效率机器人库 

[YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) : 提供SDK

[AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus) ： 回复语录提供

[Lolicon API](https://api.lolicon.app/#/setu) : 色图
