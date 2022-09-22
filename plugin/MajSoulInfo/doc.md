
##雀魂功能配置
```yaml
qhpt: true          # 是否启用查询雀魂PT功能
qhinfo: true        # 是否启用查询雀魂信息功能
qhsl: true          # 是否启用模拟雀魂抽卡
qhyb: true          # 是否启用查询雀魂月报功能
qhpaipu: true       # 是否启用查询雀魂牌谱功能
autoquery: true     # 是否启用自动查询
searchfrequency: 6  # 牌谱查询频率,建议为6,必须为整数
dailydrawcount: 3   # 每个用户每天抽卡次数上限
query_limit: 10     # 同时查询的最大请求数量
linknum: -1         # 选择的结点, 有效值为1-5, 填其他值会自动获取结点,默认-1
link_update: true   # 链路是否自动更新,仅在linknum无效时启用
link_updatetime: "2:33" # 节点更新时间，采用的是根据 “:" 进行字符串分割
                    # 可以用 *:20表示 在每小时20分自动更新, 
                    # 用 1/2:00表示从1点开始,每2小时,在0分时自动更新自动更新
silence_CLI: false  # 启用时减少控制台的信息输出
broadcast: "image"  # 广播类型,发送图片还是文本,或者是混合
                    #可选参数 'image','img','str','txt','text','mix','mixed'
 # 分别在在某群禁用 相关功能
disptgroup:
  - 0
disinfogroup:
  - 0
disslgroup:
  - 0
disybgroup:
  - 0
dispaipugroup:
  - 0
```

## 雀魂十连的配置 drawcards.yml 
### 我会不定期更新配置和图片资源


```yaml
# 示例
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

## 指令介绍


## 雀魂相关

**雀魂相关的指令基本都以“ 雀魂”开头，基本格式为 `雀魂xx [参数]`**

### **最重要的指令 `qhpt`**

 ```
qhpt / 雀魂分数 / 雀魂pt [玩家名]  ({3/4})  (index)
 ```

 查询该玩家的雀魂段位分 ( 最后两个参数一般不需要，下面会给出使用实例 )

只有玩家名作为参数时是**模糊查询**，可能会查到多名玩家，继而导致数据库注册有误。**精确查询**请加上对局类型和序号

 **该指令用于向本地数据库注册玩家信息，后面的指令查询雀魂的玩家时都需要先用 qhpt 查一次**

得到的反馈中有查询的玩家与目标玩家不匹配的问题 ( **比如 ID 比较短，刚好是别人的前缀** ) ,会查询到多人

```
#假如是四麻

qhpt 豆本豆豆
```
此时会返回两个人 ( 豆本豆豆 和 豆本豆豆奶奶),而我的目标是前者，可以通过以下指令来获取指定玩家

```
qhpt 豆本豆豆 4 1
# 1 可以省略，默认是取第一个
```
同时，由于该玩家不打三麻，我的默认查询机制是先三麻后四麻。在三麻会查询到一个新的用户 ( 豆本豆豆奶 )，由上可知这不是我的目标玩家。所以会影响我后续的指令匹配。

当`qhpt`指令带后面两个参数( 查询类型 和 查询顺序 )时,可以覆盖之前绑定的用户。

还是以豆本豆豆为例，如果我不小心用普通指令进行查询，玩家匹配错误，可以通过带参数查询来更改绑定的用户

具体的 index ( 查询顺序 ) 请去雀魂牌谱屋搜索

index 是从 `1` 开始的，即 `第一个用户的 index 是 1`

<br>

---

<br>

```
qhsl/雀魂十连 ({限时/常驻}) 
```

来一次模拟雀魂十连，可以在 MajSoulInfo的 [drawcards.yml](../config/MajSoulInfo/drawcards.yml) 中配置哪些装扮或者角色进行up

***我并不清楚雀魂抽卡机制到底是怎么样的，我只是根据它公布的规则的来设计了这个抽卡。十连保底给一个紫礼物，存在绿礼物***

*有兴趣可以帮我完善一下抽卡功能,帮我写几个卡池*

*图一乐就好了，别计较池子里有什么东西了*

*有人说角色爆率偏高,那用猫粮公布的概率抽卡就是这样的*

```
qhgetmyqhsl
```
获取我的抽卡总结

```
qhadd / 雀魂添加关注 [玩家名] 
```

将一个玩家添加至自动查询，有新对局记录时会广播

```
qhgetwatch / 雀魂获取本群关注 
```

获取本群所有的雀魂关注的玩家

```
qhdel / 雀魂删除关注 [玩家名] 
```

将一个玩家从**本群的**自动查询中移除，**不再**在此群自动广播对局该玩家的对局记录

```
qhpaipu / 雀魂最近对局 [玩家名] {3/4} ({1-10})
```

查询一个玩家最近n场3/4人对局记录

```
qhinfo / 雀魂玩家详情 [玩家名] {3/4}  {'基本','立直','血统','更多','all'} {'all', '金', '金东', '金南', '玉', '玉东', '玉南', '王', '王座', '王座东', '王座南'}
```

查询一个玩家的详细数据

```
qhyb / 雀魂月报 [玩家名] ({3/4}) ([YYYY-m])
```
获取一个玩家某月3/4麻月报，时间格式为 2022-3，可以不带对局类型参数和时间参数，默认为四麻和当前月份

当只有玩家名作为参数时，可以不需要空格，如 `qhybxyshu`


```
qhdisable/enable qhpt/qhsl/qhyb ......
```
禁用 / 启用 该群指令 `qhpt/qhsl/qhyb` 等等指令的使用

----
 <font size=5>Tag相关</font>
```
qhtagon [玩家名] [Tag]
```

在本群内给某个玩家打上Tag，方便将账号和群友进行对应

```
qhtagoff [玩家名] {Tag}
```

当 Tag 给定时，删除 玩家a 的 b Tag

当没有 Tag 时，删除 玩家a的所有Tag

```
qhtaglist {target}
```
返回本群的 <font color="green">玩家名-Tag 表</font>  

当没有指定target的时候，默认输出全部; 

```
例: qhtaglist
```

当 target 存在时，输出 <font color="blue">玩家名 = target</font> 的对应表;

```
例: qhtaglist  xyshu
```

当 target 存在 且 以<font color="red"> tag= </font>或 <font color="red">tagname=</font>开头时(不区分大小写),输出 <font color="blue">Tag = target</font> 的对应表```例: qhtaglist  TaG=NekoRabi```

---

```
qhfreshdb
```

*<font color='blue'>私聊指令</font>* 刷新雀魂牌谱数据库,实际上就是手动做了一次查询

```
qhfreshlink
```

*<font color='blue'>私聊指令</font>* 自动选择当前最好的牌谱屋链路

---