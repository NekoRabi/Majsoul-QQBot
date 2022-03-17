# 重构基本完成了

# Majsoul-QQBot
一个基于YiriMirai的QQ机器人，有查询雀魂玩家信息、播报牌谱
、玩家详情、模拟十连、入群欢迎 和 制作图片等功能。

最初目的是上面这样，但是，后续会添加更多的功能来让机器人更加完善。

 [指令帮助](./command_help.md)

# 效果展示

## 十连模拟抽卡

![雀魂十连](./other/效果展示/雀魂十连.png)

## 查一个玩家的数据

![雀魂玩家详情](./other/效果展示/雀魂玩家详情.png)

## 自动播报对局信息

![自动抓取牌谱](./other/效果展示/自动抓取牌谱.png)


## 查询玩家的最近对局情况

![最近对局](./other/效果展示/最近对局.png)

# 如何实现
数据来自[雀魂牌谱屋](https://amae-koromo.sapk.ch/)，通过定时爬取来获取牌谱。


# 如何使用
需要先安装 mirai 和 mirai-api-http，在mirai-api-http的配置文件中修改adapter和adapterSettings，再下载本程序，在config.yml中配置好相关参数后就可以直接使用命令行启动。

如果Mirai安装了`chat-command`，建议在Mirai控制台界面中输入 `/perm permit u* console:command.help`，来禁用Mirai的帮助输出。

可以参考 YiriMirai 的[官方文档](https://yiri-mirai.wybxc.cc/docs/quickstart)的快速部署。

可以使用 ``` pip install -r requirements.txt``` 来快速安装所需依赖。

我提供了自己的Mirai-Http配置，可以直接进行复制和替换。

本程序 `WebSocketAdapter` 的端口号为 `17280`。 

我也提供了自己的Mirai，可以直接使用

# 配置文件

中文如果出现乱码，可以使用 VSCode “通过编码重新打开” ，选择编码为GBK。
### config.yml
 ``` 注意, '冒号' (:) 后必须有空格 ```
 ```

### 请注意 ， 冒号(:)和横线(-)  后面必须要有用空格
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
botconfig:
  botname: ''  # 机器人的昵称，用于和机器人聊天交互
  qq: 123456  # 请改成机器人的QQ号
commandpre: '' # 指令前缀
searchfrequency: 6 # 雀魂牌谱查询频率(单位: 分钟)，不要太快,最好为60的因数
                   # 建议为 5 或 6 分钟
                   # 网络请求很耗时间,尤其是数据库用户很多的时候，在查询的过程中
                   # 机器人不会对外响应，所有操作将排队
mutegrouplist: # 屏蔽某群的消息(目前没做)
- 0
settings: # 各项开关设置
  autogetpaipu: true  # 自动抓取牌谱并广播,默认开启
  autowelcome: true # 自动欢迎新人入群,默认开启
  r18talk: true # 管理员应有独特对话的权力，对吧
  setu: false # 开关色图功能
              # 但是大概率会因为网络请求超时而发不出来
welcomeinfo: 
# 欢迎消息,新人入群会从下面随机选择一条发送。 
# %ps% 用于指代新入群的用户名字, %gn% 用于指代加入的群的群名字
- 欢迎 %ps% 加入群聊 %gn%
whitelist: # 白名单(功能暂无)
- 0

 ```
## 回复文本相关
### 以 reply.json 为例
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
 - 入群欢迎
 - 摸头、互亲、举牌、色图等图片相关功能
 - 自定义回复
 - 以后会有更多

 # 存在的问题
 1. ~~查询玩家信息的时候仍然会卡死，可能是由于超时。~~（已解决）
 2. 自动抓取牌谱时存在较长时间的无响应
 3. config.yml编辑后乱码。 ~~（基本候是将 UTF-8 编码保存为 GBK 或者反过来）~~
 解决办法: 将config.yml用GBK编码打开并保存 
 4. 涩图请求超时

 # 开发计划

  [ ] 增加何切支持

  [ ] 增加对天凤的支持

  [ ] `要在自动查询牌谱时仍然能够对外相应`

  [ ] 更多更多的功能

  [?] 将所有功能都写进配置文件，提供高度自定义

  [ ] 打包成exe

  [ ] 做一份完整的说明书

# 联系方式
QQ:1215791340 验证消息： 可爱的拉克丝

欢迎提交 需求、BUG、问题，也可以找我询问项目相关的问题

# 开源协议
由于 [mirai](https://github.com/mamoe/mirai) 、 mirai-api-http 、 [YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) 均采用了 AGPL-3.0 开源协议，本项目同样采用 AGPL-3.0 协议。

请注意，AGPL-3.0 是传染性协议。如果你的项目引用了或改造了我的项目，请在发布时公开源代码，并同样采用 AGPL-3.0 协议。

# 项目支持
[Mirai](https://github.com/mamoe/mirai) : 提供 QQ Android 协议支持的高效率机器人库 

[YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) : 提供SDK

[Yuzi_project](https://github.com/MEYUYU/yuzi-project) : 作者提供了大量帮助

[Saya_plugins_collection](https://github.com/SAGIRI-kawaii/saya_plugins_collection) : 移植功能

[AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus) ： 回复语录提供

[Lolicon API](https://api.lolicon.app/#/setu) : 色图
