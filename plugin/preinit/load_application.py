import yaml
import os
import json

config = {}
replydata = {}


def load_config() -> dict:
    try:
        with open(r'./config.yml') as f:
            config: dict = yaml.safe_load(f)
            print(config)
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
        if len(welcomeinfo) == 0:
            print("入群欢迎文本不存在，该功能将关闭")
            config['settings']['autowelcome'] = False
        return config
    except Exception as e:
        print("文件打开错误，尝试生成初始文件中...")
        with open(r'./config.yml', 'w') as f:
            yaml.dump(dict(admin=[1215791340], whitelist=[1215791340], blacklist=[0], mutegrouplist=[0],
                           welcomeinfo=["欢迎%ps%加入%gn%"], alarmclockgroup=[566415871],
                           silencegroup=[0], commandpre="", searchfrequency=6,
                           botconfig=dict(qq=3384437741, botname="拉克丝", ),
                           repeatconfig=dict(repeatQ=20, repeatmsg=1, interruptQ=0.5, interruptQQ=0.1),
                           adapter=dict(verify_key='xyshu123', host='localhost',
                                        port=17280),
                           settings=dict(autogetpaipu=True, autowelcome=True, r18talk=True, setu=False, silence=False)),
                      f, allow_unicode=True)
            print("默认文件生成完成，请重新启动。")
            exit(0)


def load_replydata() -> dict:
    if os.path.exists(r"./data/commonreply.json"):
        with open(r"./data/commonreply.json", 'r', encoding="utf-8") as commonreply:
            replydata['common'] = json.load(commonreply)
    else:
        print("回复文本不存在")
        replydata['common'] = {"你好": ["你好"]}

    if os.path.exists(r"./data/hyperreply.json"):
        with open(r"./data/hyperreply.json", 'r', encoding="utf-8") as r18reply:
            replydata['r18'] = json.load(r18reply)
    else:
        print("r18回复文本不存在")
        replydata['r18'] = {"你好": ["爱你"]}

    if os.path.exists(r"./data/black_user_reply.yml"):
        with open(r"./data/black_user_reply.yml", encoding="utf-8") as blackreply:
            replydata['blackuser'] = yaml.safe_load(blackreply)
    else:
        print("黑名单回复文本不存在")
        replydata['blackuser'] = {"你好": ["不好"]}

    if os.path.exists(r"./data/nudgedata.yml"):
        with open(r'./data/nudgedata.yml', encoding="utf-8") as nudegfile:
            replydata['nudgedate'] = yaml.safe_load(nudegfile)
    else:
        print("摸头文本不存在")
        replydata['nudgedate'] = ["摸摸"]

    if os.path.exists(r"./data/mismatch.yml"):
        with open(r'./data/mismatch.yml', encoding="utf-8") as mismatch:
            replydata['mismatch'] = yaml.safe_load(mismatch)
    else:
        print("摸头文本不存在")
        replydata['mismatch'] = dict(admin=["主人有事吗?"], common=['你在叫我吗?'])
    return replydata
