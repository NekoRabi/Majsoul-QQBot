import os
import sys

from utils import text_to_image
from utils.cfg_loader import loadcfg_from_file, w_cfg_to_file

__all__ = ['config', 'replydata', 'admin', 'master', 'commandpre', 'commands_map', 'load_replydata', 'load_commands',
           'load_config', 'create_helpimg', 'create_init_config']

config = {}
replydata = {}
_syskey = {'admin', 'whitelist', 'blacklist', 'settings', 'welcomeinfo', 'alarmclockgroup', 'commandpre', 'botconfig',
           'silencegroup', 'repeatconfig', 'norepeatgroup', 'qhsettings', 'nudgeconfig', 'loglevel', 'master',
           'voicesetting', 'mutegrouplist', 'setugroups', 'welcomeinfo', 'replyimgpath', 'searchfrequency'}


def load_config() -> dict:
    return config


def load_replydata() -> dict:
    if os.path.exists(r"./data/reply/commonreply.json"):
        replydata['common'] = loadcfg_from_file(r"./data/reply/commonreply.json", filetype='json')

    else:
        print("回复文本不存在")
        replydata['common'] = {"你好": ["你好"]}

    if os.path.exists(r"./data/reply/hyperreply.json"):
        replydata['r18'] = loadcfg_from_file(r"./data/reply/hyperreply.json", filetype='json')
    else:
        print("r18回复文本不存在")
        replydata['r18'] = {"你好": ["爱你"]}

    if os.path.exists(r"./data/reply/black_user_reply.yml"):
        replydata['blackuser'] = loadcfg_from_file(r"./data/reply/black_user_reply.yml")
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


def load_commands() -> dict:
    try:
        all_commands = loadcfg_from_file(r'./config/command.yml')
        return all_commands
    except Exception as _e:
        print(f"发生未知错误{_e}")


def create_helpimg():
    _help = loadcfg_from_file(r'./data/sys/help.yml')
    grouphelp = _help['grouphelp']
    friendhelp = _help['friendhelp']
    text_to_image(path='grouphelp.png', text=grouphelp)
    text_to_image(path='friendhelp.png', text=friendhelp)


def create_init_config():
    """生成默认配置"""
    sys_config = dict(admin=[0], whitelist=[0], blacklist=[0], mutegrouplist=[0], setugroups=[0],
                      welcomeinfo=["欢迎%ps%加入%gn%"], alarmclockgroup=[0],
                      silencegroup=[0], norepeatgroup=[0], disnudgegroup=[0], commandpre="", searchfrequency=6,
                      master=0, loglevel="INFO", replyimgpath='fox', botconfig=dict(qq=123456, botname=""),
                      repeatconfig=dict(
                          repeatQ=20, repeatmsg=1, interruptQ=0.5, interruptQQ=0.1, autoreply=True, kwreply=True),
                      adapter=dict(verify_key='NekoRabi',
                                   host='localhost', port=17280),
                      settings=dict(autogetpaipu=True, autowelcome=True, help=True, r18talk=True, nudgereply=True,
                                    setu=False, silence=False, norepeat=False, voice=False, saveflashimg=True),
                      voicesettings=dict(codec='mp3', volumn=1, speed=0.85, voicetype=1002, private=True,
                                         secretId='',
                                         secretKey=''),
                      qhsettings=dict(qhpt=True, qhinfo=True, qhsl=True, qhyb=True, qhpaipu=True, disptgroup=[0],
                                      disinfogroup=[0], disslgroup=[0], disybgroup=[0], disautoquerygroup=[0],
                                      dispaipugroup=[0]))
    w_cfg_to_file(sys_config, r'./config/config.yml')


try:
    config = loadcfg_from_file(r'./config/config.yml')
    if not config:
        print("生成初始文件中...")
        create_init_config()
        print("默认文件生成完成，请重新启动")
        sys.exit(0)
    for key in _syskey:
        if key not in config.keys():
            print(f"缺少关键字 {key}，尝试生成初始文件中...")
            create_init_config()
            print("默认文件生成完成，请重新启动")
            sys.exit(0)
    for k, v in config.items():
        print(k, v)
    _settings = config['settings']
    _welcomeinfo = config.get('welcomeinfo', [])
    _botconfig = config['botconfig']
    _botname = _botconfig['botname']
    _voicesetting = config['voicesetting']
    master = config.get('master', 0)
    replydata['replyimgpath'] = config['replyimgpath']
    if master == 0:
        print('请输入机器人主人 ( master )')
    if _settings['voice']:
        if _voicesetting['secretId'].strip() == '' or _voicesetting['secretKey'] == '':
            print('请在填写语音设置后,再开启语音功能  现已将语音功能关闭')
            _settings['voice'] = False
            w_cfg_to_file(content=config, path=r'./config/config.yml')
    if len(_welcomeinfo) == 0:
        print("入群欢迎文本不存在，该功能将关闭")
        config['settings']['autowelcome'] = False
except Exception as e:
    print(f'{e}')
    print("文件打开错误，尝试生成初始文件中...")
    create_init_config()
    print("默认文件生成完成，请重新启动")
    sys.exit(0)

commandpre = config.get('commandpre', '')
commands_map = load_commands()
admin = config['admin']
if master != 0 and master not in admin:
    admin.append(master)
