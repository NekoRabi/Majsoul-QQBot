import yaml
import os
import json
from utils.text_to_img import text_to_image

config = {}
replydata = {}

kargs = {'admin', 'whiteList', 'settings', 'welcomeinfo', 'alarmclockgroup', 'commandpre', 'botconfig', 'botname',
         'silencegroup', 'repeatconfig', 'norepeatgroup', 'qhsettings', 'nudgeconfig', 'loglevel', 'master'}


def load_config() -> dict:
    try:
        with open(r'./config/config.yml', encoding="gbk") as f:
            config = yaml.safe_load(f)
            # for key in kargs:
            #     if key not in config.keys():
            #         raise Exception
            for k, v in config.items():
                print(k, v)
            admin = config['admin']
            whiteList = config['whitelist']
            settings = config['settings']
            welcomeinfo = config['welcomeinfo']
            alarmclockgroup = config['alarmclockgroup']
            commandpre = config['commandpre']
            botconfig = config['botconfig']
            botname = botconfig['botname']
            silencegroup = config['silencegroup']
            repeatconfig = config['repeatconfig']
            norepeatgroup = config['norepeatgroup']
            qhsettings = config['qhsettings']
            nudgeconfig = config['nudgeconfig']
            loglevel = config['loglevel']
            master = config['master']
            replydata['replyimgpath'] = config['replyimgpath']
            if master == 0:
                print('请输入机器人主人 ( master )')
        if len(welcomeinfo) == 0:
            print("入群欢迎文本不存在，该功能将关闭")
            config['settings']['autowelcome'] = False
        return config
    except Exception as e:
        print(f'{e} 缺失')
        print("文件打开错误，尝试生成初始文件中...")
        with open(r'./config.yml', 'w', encoding="gbk") as f:
            yaml.dump(dict(admin=[0], whitelist=[0], blacklist=[0], mutegrouplist=[0], setugroups=[0],
                           welcomeinfo=["欢迎%ps%加入%gn%"], alarmclockgroup=[0],
                           silencegroup=[0], norepeatgroup=[0], disnudgegroup=[0], commandpre="", searchfrequency=6,
                           master=0, loglevel="INFO", replyimgpath='fox', botconfig=dict(qq=123456, botname=""),
                           repeatconfig=dict(
                               repeatQ=20, repeatmsg=1, interruptQ=0.5, interruptQQ=0.1),
                           adapter=dict(verify_key='NekoRabi',
                                        host='localhost', port=17280),
                           settings=dict(autogetpaipu=True, autowelcome=True, r18talk=True, nudgereply=True, setu=False,
                                         silence=False, norepeat=False, asyreptile=False,voice=False),
                           voicesettings=dict(volumn=1,speed=0.85,secretId='',secretKey=''),
                           qhsettings=dict(qhpt=True, qhinfo=True, qhsl=True, qhyb=True, qhpaipu=True, disptgroup=[0],
                                           disinfogroup=[0], disslgroup=[0], disybgroup=[0], disautoquerygroup=[0],
                                           dispaipugroup=[0])),
                      f, allow_unicode=True)
            print("默认文件生成完成，请重新启动")
            exit(0)


def load_replydata() -> dict:
    if os.path.exists(r"./data/reply/commonreply.json"):
        with open(r"./data/reply/commonreply.json", 'r', encoding="utf-8") as commonreply:
            replydata['common'] = json.load(commonreply)
    else:
        print("回复文本不存在")
        replydata['common'] = {"你好": ["你好"]}

    if os.path.exists(r"./data/reply/hyperreply.json"):
        with open(r"./data/reply/hyperreply.json", 'r', encoding="utf-8") as r18reply:
            replydata['r18'] = json.load(r18reply)
    else:
        print("r18回复文本不存在")
        replydata['r18'] = {"你好": ["爱你"]}

    if os.path.exists(r"./data/reply/black_user_reply.yml"):
        with open(r"./data/reply/black_user_reply.yml", encoding="utf-8") as blackreply:
            replydata['blackuser'] = yaml.safe_load(blackreply)
    else:
        print("黑名单回复文本不存在")
        replydata['blackuser'] = {"你好": ["不好"]}

    if os.path.exists(r"./data/reply/nudgedata.yml"):
        with open(r'./data/reply/nudgedata.yml', encoding="utf-8") as nudegfile:
            replydata['nudgedata'] = yaml.safe_load(nudegfile)
    else:
        print("摸头文本不存在")
        replydata['nudgedata'] = ["摸摸"]

    if os.path.exists(r"./data/reply/mismatch.yml"):
        with open(r'./data/reply/mismatch.yml', encoding="utf-8") as mismatch:
            replydata['mismatch'] = yaml.safe_load(mismatch)
    else:
        print("摸头文本不存在")
        replydata['mismatch'] = dict(admin=["主人有事吗?"], common=['你在叫我吗?'])

    if os.path.exists(fr"./data/reply/img/{replydata['replyimgpath']}"):
        imgpathlist_dir = os.listdir(fr"./data/reply/img/{replydata['replyimgpath']}")
        imgpath = []
        for imgname in imgpathlist_dir:
            imgpath.append(imgname)
        replydata['img'] = imgpath
    else:
        replydata['img'] = []
    replydata['suffix'] = ['']
    return replydata


def create_helpimg():
    grouphelp = "指令帮助 ()内为可选项,[]为必选项,{}为可用参数,<>为类型:\n" \
                "qhpt / 雀魂分数 / 雀魂pt [玩家名] (3/4) (序号):查询该玩家的段位分\n" \
                "qhsl / 雀魂十连 ({限时/常驻}) :来一次模拟雀魂十连\n" \
                "qhadd / 雀魂添加关注 [玩家名] :将一个玩家添加至雀魂自动查询，有新对局记录时会广播\n" \
                "qhgetwatch / 雀魂获取本群关注 :获取本群所有的雀魂关注的玩家\n" \
                "qhdel / 雀魂删除关注 [玩家名] :将一个玩家从雀魂自动查询中移除，不再自动广播对局记录\n" \
                "qhpaipu / 雀魂最近对局 [玩家名] [{3/4}] ({1-10}) :查询一个玩家最近n场3/4人对局记录\n" \
                "qhinfo / 雀魂玩家详情 [玩家名] [{3/4}] ({基本/立直/血统/all}):查询一个玩家的详细数据\n" \
                "qhyb / 雀魂月报 [玩家名] [{3/4}] [yyyy-mm] :查询一个玩家yy年mm月的3/4麻对局月报\n" \
                "thpt / 天凤pt / 天凤分数 [玩家名] : 查询玩家的天凤pt ( 但该功能还存在问题\n" \
                "thadd / 天凤添加关注 [玩家名] :将一个玩家添加指天凤的自动查询，有新对局会广播\n" \
                "thdel / 天凤删除关注 [玩家名] :将一个玩家从天凤自动查询中移除，不再自动广播对局记录\n" \
                "thgetwatch / 天凤获取本群关注 :获取本群所有的天凤关注的玩家\n" \
                "举牌 [<文本>] :将文本写在举牌小人上发出来，最多40字\n" \
                "亲/亲亲 @用户 : 两人互亲\n" \
                "[A]鸡打.  /  我超[A]. : 返回一段主体为A发病文\n" \
                "摸/摸摸/摸头 @用户 : 摸某人头\n" \
                "重开 / remake : 异世界转生\n" \
                "bw [<文本>] [<图片>] : 返回一张黑白处理后的图片，底部有一行文字\n" \
                "签到 : 顾名思义，就是签到\n" \
                "项目地址 : 获取项目链接\n"
    adminhelp = "私聊指令:\n" \
                "addadmin / deladmin QQ号 :添加或者删除机器人管理员\n" \
                "addwhitelist /delwhitelist QQ号 :修改白名单\n" \
                "addblacklist / delblacklist QQ: 修改黑名单\n" \
                "ping :ping一下服务器,用于验证机器人存活\n" \
                "silence on/true/off/false :开启全局沉默模式，减少信息输出\n" \
                "freshqh : 刷新本地雀魂牌谱数据库\n" \
                "群管理指令:\n" \
                "open/enable/开启 涩图/色图/setu : 开启本群色图功能\n" \
                "close/disable/关闭 涩图/色图/setu : 关闭本群色图\n" \
                "disable/enable 【雀魂指令】 :关闭本群某项雀魂功能\n" \
                "silence on/true/off/false :开启本群沉默模式，减少信息输出\n" \
                "norepeat on/true/……  : 开启或关闭本群复读功能\n" \
                "" \
                "项目地址 : 获取项目链接\n"
    text_to_image(path='grouphelp.png', text=grouphelp)
    text_to_image(path='adminhelp.png', text=adminhelp)
