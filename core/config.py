"""
:Author:  NekoRabi
:Create:  2022/9/18 3:12
:Update: /
:Describe: 机器人配置文件
:Version: 0.6.5
"""
import sys

from utils import text_to_image
from utils.cfg_loader import *

__all__ = ['config', 'replydata', 'admin', 'master', 'commandpre', 'commands_map', 'load_replydata', 'load_commands',
           'load_config', 'create_helpimg', 'create_init_config']

config = {}
replydata = {}
_syskey = {'admin', 'whitelist', 'blacklist', 'settings', 'welcomeinfo', 'alarmclockgroup', 'commandpre', 'botconfig',
           'silencegroup', 'nudgeconfig', 'loglevel', 'master', 'mutegrouplist',
           'welcomeinfo', 'replyimgpath'}


def load_config() -> dict:
    """加载配置文件"""
    return config


def load_replydata() -> dict:
    """加载回复"""
    if os.path.exists(r"./data/reply/commonreply.json"):
        replydata['common'] = read_file(r"./data/reply/commonreply.json", filetype='json')

    else:
        print("回复文本不存在")
        replydata['common'] = {"你好": ["你好"]}

    if os.path.exists(r"./data/reply/hyperreply.json"):
        replydata['r18'] = read_file(r"./data/reply/hyperreply.json", filetype='json')
    else:
        print("r18回复文本不存在")
        replydata['r18'] = {"你好": ["爱你"]}

    if os.path.exists(r"./data/reply/black_user_reply.yml"):
        replydata['blackuser'] = read_file(r"./data/reply/black_user_reply.yml")
    else:
        print("黑名单回复文本不存在")
        replydata['blackuser'] = {"你好": ["不好"]}

    if os.path.exists(r"./data/reply/nudgedata.yml"):
        replydata['nudgedata'] = read_file(r'./data/reply/nudgedata.yml')
    else:
        print("摸头文本不存在")
        replydata['nudgedata'] = ["摸摸"]

    if os.path.exists(r"./data/reply/mismatch.yml"):
        replydata['mismatch'] = read_file(r'./data/reply/mismatch.yml')
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
    """获取系统指令"""
    try:
        all_commands = read_file(r'./config/command.yml')
        return all_commands
    except Exception as _e:
        print(f"发生未知错误{_e}")


def create_helpimg():
    """生成帮助图片"""
    _help = read_file(r'./data/sys/help.yml')
    grouphelp = _help['grouphelp']
    friendhelp = _help['friendhelp']
    text_to_image(text=grouphelp, path='grouphelp.png')
    text_to_image(text=friendhelp, path='friendhelp.png')


def create_init_config():
    """生成默认配置"""
    sys_config = dict(admin=[0], whitelist=[0], blacklist=[0], mutegrouplist=[0],
                      welcomeinfo=["欢迎%ps%加入%gn%"], alarmclockgroup=[0],
                      silencegroup=[0], disnudgegroup=[0], commandpre="",
                      master=0, loglevel="INFO", replyimgpath='fox', botconfig=dict(qq=123456, botname=""),
                      nudgeconfig=dict(disnudgegroup=[0], sendnudgechance=0.3, supernudgequantity=10,
                                       supersendnudgechance=0.2),
                      adapter=dict(verify_key='NekoRabi',
                                   host='localhost', port=17280),
                      settings=dict(autowelcome=True, help=True, r18talk=True, nudgereply=True,
                                    silence=False,  saveflashimg=True))
    write_file(sys_config, r'./config/config.yml')


try:
    config = read_file(r'./config/config.yml')
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
    master = config.get('master', 0)
    replydata['replyimgpath'] = config['replyimgpath']
    if master == 0:
        print('请输入机器人主人 ( master )')
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
