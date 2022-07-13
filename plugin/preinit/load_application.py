import yaml
import os
import json
from utils.text_to_img import text_to_image
from utils.cfg_loader import loadcfg_from_file

config = {}
replydata = {}
kargs = {'admin', 'whiteList', 'settings', 'welcomeinfo', 'alarmclockgroup', 'commandpre', 'botconfig', 'botname',
         'silencegroup', 'repeatconfig', 'norepeatgroup', 'qhsettings', 'nudgeconfig', 'loglevel', 'master','voicesetting'}


def load_config() -> dict:
    try:
        with open(r'./config/config.yml', encoding='utf-8') as f:
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
            voicesetting = config['voicesetting']
            master = config['master']
            replydata['replyimgpath'] = config['replyimgpath']
        if master == 0:
            print('请输入机器人主人 ( master )')
        if settings['voice']:
            if voicesetting['secretId'].strip() == '' or voicesetting['secretKey'] == '':
                print('请在填写语音设置后,再开启语音功能  现已将语音功能关闭')
                settings['voice'] = False
                with open(r'./config/config.yml', 'w', encoding='utf-8') as file:
                    yaml.dump(config, file, allow_unicode=True)
        if len(welcomeinfo) == 0:
            print("入群欢迎文本不存在，该功能将关闭")
            config['settings']['autowelcome'] = False
        return config
    except Exception as e:
        print(f'{e} 缺失')
        print("文件打开错误，尝试生成初始文件中...")
        with open(r'./config/config.yml', 'w', encoding='utf-8') as f:
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
                           voicesettings=dict(volumn=1,speed=0.85,voicetype=1002,private=True,secretId='',secretKey=''),
                           qhsettings=dict(qhpt=True, qhinfo=True, qhsl=True, qhyb=True, qhpaipu=True, disptgroup=[0],
                                           disinfogroup=[0], disslgroup=[0], disybgroup=[0], disautoquerygroup=[0],
                                           dispaipugroup=[0])),
                      f, allow_unicode=True)
            print("默认文件生成完成，请重新启动")
            exit(0)


def load_replydata() -> dict:
    if os.path.exists(r"./data/reply/commonreply.json"):
        replydata['common'] =  loadcfg_from_file(r"./data/reply/commonreply.json",filetype='json')

    else:
        print("回复文本不存在")
        replydata['common'] = {"你好": ["你好"]}

    if os.path.exists(r"./data/reply/hyperreply.json"):
        replydata['r18'] = loadcfg_from_file(r"./data/reply/hyperreply.json",filetype='json')
    else:
        print("r18回复文本不存在")
        replydata['r18'] = {"你好": ["爱你"]}

    if os.path.exists(r"./data/reply/black_user_reply.yml"):
        replydata['blackuser'] = loadcfg_from_file(r"./data/reply/black_user_reply.yml")
        with open(r"./data/reply/black_user_reply.yml", encoding="utf-8") as blackreply:
            replydata['blackuser'] = yaml.safe_load(blackreply)
    else:
        print("黑名单回复文本不存在")
        replydata['blackuser'] = {"你好": ["不好"]}

    if os.path.exists(r"./data/reply/nudgedata.yml"):
        replydata['nudgedata'] = loadcfg_from_file(r'./data/reply/nudgedata.yml')
    else:
        print("摸头文本不存在")
        replydata['nudgedata'] = ["摸摸"]

    if os.path.exists(r"./data/reply/mismatch.yml"):
        replydata['mismatch'] = loadcfg_from_file(r'./data/reply/mismatch.yml')
        # with open(r'./data/reply/mismatch.yml', encoding="utf-8") as mismatch:
        #     replydata['mismatch'] = yaml.safe_load(mismatch)
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

def load_commands() ->dict:
    try:
        all_commands =loadcfg_from_file(r'./config/command.yml')
        return all_commands
    except Exception as e:
        print(f"发生未知错误{e}")

def create_helpimg():
    help = loadcfg_from_file(r'./data/sys/help.yml')
    grouphelp = help['grouphelp']
    privatehelp = help['privatehelp']
    text_to_image(path='grouphelp.png', text=grouphelp)
    text_to_image(path='adminhelp.png', text=privatehelp)
