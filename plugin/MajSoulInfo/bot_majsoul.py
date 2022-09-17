"""
:Author:  NekoRabi
:Create:  2022/8/16 16:47
:Update: /
:Describe: 负责雀魂功能与机器人的交互
:Version: 0.6.1
"""
import datetime
import re

from mirai import GroupMessage, Plain, FriendMessage

from core import bot, config, commandpre, scheduler
from plugin.MajSoulInfo.majsoulinfo import majsoul
from plugin.MajSoulInfo.mergeimgs import mergeimgs
from utils import text_to_image
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender
from utils.bufferpool import *
from utils.cfg_loader import write_file, read_file
from utils.get_groupmember_authority import is_having_admin_permission

__all__ = ['disableqhplugin', 'enableqhplugin', 'qhpt', 'getrecentqhpaipu', 'getplayerdetails', 'getqhmonthreport',
           'getqhwatcher', 'addmajsoulwatch', 'delmajsoulwatch', 'qhdrawcards', 'getmyqhdrawcards',
           'clearmajsoulwatcher', 'qhaddtag', 'qhdeltag', 'qhtagoperate', 'qhlisttag', 'asyqh_autopaipu',
           'freshqhpaipu', 'guan_wang']
admin = config.get('admin')
# qhsettings = config.get('qhsettings')
master = config.get('master')

qhsettings = read_file(r'./config/MajSoulInfo/config.yml')

_qhcmd = read_file(r'./config/MajSoulInfo/command.yml')


@bot.on(GroupMessage)
async def disableqhplugin(event: GroupMessage):
    """
    禁用雀魂指令
    :param event:
    :return:
    """
    if is_having_admin_permission(event) or event.sender.id in admin:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{_qhcmd['disable']}", msg.strip())
        if m:
            commandname = m.group(2)
            group = event.group.id
            if commandname in ['qhpt', '雀魂分数', '雀魂pt']:
                if group not in qhsettings['disptgroup']:
                    qhsettings['disptgroup'].append(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'查分功能禁用成功')
            elif commandname in ['qhpaipu', '雀魂最近对局']:
                if group not in qhsettings['dispaipugroup']:
                    qhsettings['dispaipugroup'].append(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'牌谱查询功能禁用成功')
            elif commandname in ['qhinfo', '雀魂玩家详情']:
                if group not in qhsettings['disinfogroup']:
                    qhsettings['disinfogroup'].append(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'雀魂玩家详情功能禁用成功')
            elif commandname in ['qhsl', '雀魂十连']:
                if group not in qhsettings['disslgroup']:
                    qhsettings['disslgroup'].append(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'模拟十连功能禁用成功')
            elif commandname in ['qhyb', '雀魂月报']:
                if group not in qhsettings['dispaipugroup']:
                    qhsettings['dispaipugroup'].append(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'牌谱查询功能禁用成功')
            else:
                return await bot.send(event, '无此功能,请重新输入参数')


@bot.on(GroupMessage)
async def enableqhplugin(event: GroupMessage):
    """
    启用雀魂指令
    :param event:
    :return:
    """
    if is_having_admin_permission(event) or event.sender.id in admin:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{_qhcmd['enable']}", msg.strip())
        if m:
            commandname = m.group(2)
            group = event.group.id
            if commandname in ['qhpt', '雀魂分数', '雀魂pt']:
                if group in qhsettings['disptgroup']:
                    qhsettings['disptgroup'].remove(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'查分功能启用成功')
            elif commandname in ['qhpaipu', '雀魂最近对局']:
                if group in qhsettings['dispaipugroup']:
                    qhsettings['dispaipugroup'].remove(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'牌谱查询功能启用成功')
            elif commandname in ['qhinfo', '雀魂玩家详情']:
                if group in qhsettings['disinfogroup']:
                    qhsettings['disinfogroup'].remove(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'雀魂玩家详情功能启用成功')
            elif commandname in ['qhsl', '雀魂十连']:
                if group in qhsettings['disslgroup']:
                    qhsettings['disslgroup'].remove(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'模拟十连功能启用成功')
            elif commandname in ['qhyb', '雀魂月报']:
                if group in qhsettings['dispaipugroup']:
                    qhsettings['dispaipugroup'].remove(group)
                    # w_cfg_to_file(content=config, path=r'./config/config.yml')
                    write_file(content=qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await bot.send(event, f'牌谱查询功能启用成功')
            else:
                return await bot.send(event, '无此功能,请重新输入参数')


@bot.on(GroupMessage)
async def qhpt(event: GroupMessage):
    """
    查分
    :param event:
    :return:
    """
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhpt']}", msg.strip())
    if m:
        if qhsettings['qhpt'] and event.group.id not in qhsettings['disptgroup']:

            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhpt')):
                return bot.send(event, messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
            if m.group(3):
                selecttype = int(m.group(3))
                selectindex = m.group(4)
                if not selectindex:
                    selectindex = 0
                selectindex = int(selectindex)
                result = await majsoul.getcertaininfo(m.group(2), selecttype, selectindex)
            else:
                result = await majsoul.query(m.group(2))
            await bot.send(event, result)
            # if result['error']:
            #     # await bot.send(event, result['msg'])
            #     await sendMsgChain(msg=result['msg'], event=event)
            # else:
            #     await sendMsgChain(msg=messagechain_builder(imgpath=f'./images/MajsoulInfo/qhpt{m.group(2)}.png'),
            #                        event=event,
            #                        errortext=result['msg'])
            # await bot.send(event, imgpath=f'./images/MajsoulInfo/qhpt{m.group(2)}.png'))
        return


@bot.on(GroupMessage)
async def getrecentqhpaipu(event: GroupMessage):
    """查最近牌谱"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhpaipu']}", msg.strip())
    if m:
        if qhsettings['qhpaipu'] and event.group.id not in qhsettings['dispaipugroup']:

            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhpaipu')):
                return messagechain_sender(event=event,
                                           msg=messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
            playername = m.group(2)
            searchtype = m.group(3)
            searchnumber = 5
            if searchtype:
                if searchtype not in ['3', '4']:
                    return await messagechain_sender(event=event, msg='牌局参数有误，请输入 3 或 4')

                if m.group(4):
                    searchnumber = int(m.group(4))
                    if not 0 < searchnumber < 11:
                        return await bot.send(event, "牌局数量有误，最多支持10场牌局")
                result = await majsoul.getsomeqhpaipu(playername=playername, type=searchtype,
                                                      counts=searchnumber)
                # if not result.get('err', True):
                #     await sendMsgChain(event=event,
                #                        msg=messagechain_builder(imgbase64=result['img64']), errortext=result['msg'])
                # else:
                #     await sendMsgChain(event=event, msg=result['msg'])
                await messagechain_sender(event=event, msg=result)


@bot.on(GroupMessage)
async def getplayerdetails(event: GroupMessage):
    """查玩家详情"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhinfo']}", msg.strip())
    if m:
        if qhsettings['qhinfo'] and event.group.id not in qhsettings['disinfogroup']:

            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhinfo')):
                return bot.send(event, messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
            playername = m.group(2)
            selecttype = m.group(3)
            model = m.group(4)
            selectlevel = m.group(5)
            if selectlevel:
                pass
            if model is None:
                model = '基本'
            detail = await majsoul.getplayerdetail(
                playername=playername, selecttype=selecttype, model=model)
            await bot.send(event, detail)
            # if detail['error']:
            #     await bot.send(event, detail['msg'])
            # else:
            #     res = await bot.send(event,
            #                          messagechain_builder(imgpath=f'./images/MajsoulInfo/detail{playername}.png'))
            #     if res == -1:
            #         await bot.send(event, detail['msg'])
    return


@bot.on(GroupMessage)
async def getqhmonthreport(event: GroupMessage):
    """查月报"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhyb']}", msg.strip())
    if m:
        if qhsettings['qhyb'] and event.group.id not in qhsettings['disybgroup']:
            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhyb')):
                return bot.send(event, messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True, at=event.sender.id))
            playername = m.group(2)
            selecttype = m.group(3)
            year = m.group(4)
            month = m.group(5)
            report = await majsoul.getmonthreport(
                playername=playername, selecttype=selecttype, year=year, month=month)
            await bot.send(event, report)
            # if report['error']:
            #     await bot.send(event, report['msg'])
            # else:
            #     res_id = await bot.send(event,
            #                             messagechain_builder(imgpath=f'./images/MajsoulInfo/yb{playername}.png'))
            #     if res_id == -1:
            #         print(f"图片yb{playername}.png发送失败，尝试发送文本")
            #         await bot.send(event, report['msg'])
            # await bot.send(event,messagechain_builder()(imgbase64=report['imgbase64']))
    return


@bot.on(GroupMessage)
async def getqhwatcher(event: GroupMessage):
    """获取雀魂订阅"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['getwatch']}", msg.strip())
    if m:
        await bot.send(event, majsoul.getallwatcher(event.group.id))


@bot.on(GroupMessage)
async def addmajsoulwatch(event: GroupMessage):
    """加入订阅"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['addwatch']}", msg.strip())
    if m:
        if event.group.id:
            # if is_havingadmin(event):
            #     await bot.send(event, addwatch(m.group(2), event.group.id))
            # else:
            #     await bot.send(event, messagechain_builder(at=event.sender.id), text=" 抱歉，只有管理员才能这么做哦")]))
            await bot.send(event, majsoul.addwatch(m.group(2), event.group.id))


@bot.on(GroupMessage)
async def delmajsoulwatch(event: GroupMessage):
    """删除订阅"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['delwatch']}", msg.strip())
    if m:
        if event.group.id:
            # if is_havingadmin(event):
            #     await bot.send(event,
            #                    removewatch(playername=m.group(2), groupid=event.group.id))
            # else:
            #     await bot.send(event, messagechain_builder(at=event.sender.id), text=" 抱歉，只有管理员才能这么做哦")]))
            await bot.send(event, majsoul.removewatch(m.group(2), event.group.id))
    return


@bot.on(GroupMessage)
async def qhdrawcards(event: GroupMessage):
    """雀魂十连抽卡模拟"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhsl']}", msg.strip())
    if m:
        if qhsettings['qhsl'] and event.group.id not in qhsettings['disslgroup']:
            if m.group(2):
                if m.group(2) in ['限时', '限定', 'up', 'UP']:
                    result = majsoul.drawcards(userid=event.sender.id, up=True)
                    if result['error']:
                        return await bot.send(event,
                                              messagechain_builder(at=event.sender.id, text=result['resultsmsg']))
                    mergeimgs(result.get('results'), event.sender.id)
                    await bot.send(event, messagechain_builder(
                        at=event.sender.id,
                        text="抽卡结果:", imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
                    # return await bot.send(event, messagechain_builder(
                    #     at=event.sender.id),
                    #     text=result['resultsmsg'])
                    # ]))
                elif m.group(2) in ['常驻', '普通', 'common', 'normal']:
                    result = majsoul.drawcards(userid=event.sender.id, up=False)
                    if result['error']:
                        return await bot.send(event,
                                              messagechain_builder(at=event.sender.id, text=result['resultsmsg']))
                    mergeimgs(result.get('results'), event.sender.id)
                    await bot.send(event, messagechain_builder(
                        at=event.sender.id,
                        text="抽卡结果:",
                        imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
                    # return await bot.send(event, messagechain_builder(
                    #     at=event.sender.id),
                    #     text=result['resultsmsg'])
                    # ]))
                else:
                    result = majsoul.drawcards(userid=event.sender.id, up=False)
                    if result['error']:
                        return await bot.send(event,
                                              messagechain_builder(at=event.sender.id, text=result['resultsmsg']))
                    await bot.send(event,
                                   messagechain_builder(at=event.sender.id, text='参数输入有误，请输入“限时”或“常驻”，此次十连将输出常驻'))
                    mergeimgs(
                        result.get('results'), event.sender.id)
                    await bot.send(event, messagechain_builder(
                        at=event.sender.id,
                        text="抽卡结果:",
                        imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
                    # return await bot.send(event, messagechain_builder(
                    #     at=event.sender.id),
                    #     text=result['resultsmsg'])
                    # ]))
            else:
                result = majsoul.drawcards(userid=event.sender.id, up=False)
                if result['error']:
                    return await bot.send(event, messagechain_builder(at=event.sender.id, text=result['resultsmsg']))
                mergeimgs(
                    result.get('results'), event.sender.id)
                await bot.send(event, messagechain_builder(
                    at=event.sender.id,
                    text="抽卡结果:",
                    imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
        else:
            return await bot.send(event, messagechain_builder(text="此群已禁用模拟抽卡"))
    return


@bot.on(GroupMessage)
async def getmyqhdrawcards(event: GroupMessage):
    """获取抽卡记录"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['getmyqhsl']}", msg.strip())
    if m:
        return await bot.send(event, majsoul.getmycard(event.sender.id))


@bot.on(GroupMessage)
async def clearmajsoulwatcher(event: GroupMessage):
    """清空x群的雀魂订阅"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['clearwatch']}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await bot.send(event, majsoul.clearallwatch(groupid=event.group.id))
        else:
            await bot.send(event, messagechain_builder(at=event.sender.id, text=" 抱歉，只有管理员才能这么做哦"))


@bot.on(GroupMessage)
async def qhaddtag(event: GroupMessage):
    """为x群的雀魂玩家添加昵称或者是Tag"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['tagon']}", msg.strip())
    if m:
        if not m.group(3):
            return await messagechain_sender(event=event, msg=messagechain_builder(text='请输入你要添加tag哦'))
        if is_having_admin_permission(event):
            await bot.send(event,
                           majsoul.tagonplayer(playername=m.group(2), tagname=m.group(3), userid=event.sender.id,
                                               groupid=event.group.id))
        else:
            await messagechain_sender(event=event, msg=messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))


@bot.on(GroupMessage)
async def qhdeltag(event: GroupMessage):
    """删除昵称或者Tag"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['tagoff']}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            tagnames = None
            if m.group(3):
                tagnames = m.group(3)
            await bot.send(event, majsoul.tagoffplayer(playername=m.group(2), groupid=event.group.id,
                                                       userid=event.sender.id, tagname=tagnames))
        else:
            await bot.send(event, messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))


@bot.on(GroupMessage)
async def qhtagoperate(event: GroupMessage):
    """tag批量操作"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['tagopeartion']}", msg.strip())
    ope_type = 'add'
    p1 = 'NekoRabi'
    p2 = '帅哥'
    if m:
        if is_having_admin_permission(event):
            if m.group(2):
                ope_type = m.group(2).lower()
            print(ope_type)
            if ope_type not in ['cut', 'copy']:
                return
            if m.group(3):
                p1 = m.group(3)
            if m.group(4):
                p2 = m.group(4)
            # result = majsoul.tagonplayer(playername=p1, tagname=p2, userid=event.sender.id,
            #                     groupid=event.group.id)
            result = majsoul.tag_C_operation(event.group.id, p1, p2, ope_type)
            await messagechain_sender(messagechain_builder(text=result), event)


@bot.on(GroupMessage)
async def qhlisttag(event: GroupMessage):
    """获取所有Tag"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['taglist']}", msg.strip())
    if m:
        target = m.group(2)
        searchtype = 'playername'
        if target:
            if target.startswith('tag=') or target.startswith('tagname='):
                target = target.split('=', 2)[1]
                searchtype = 'tagname'
        await messagechain_sender(event=event, msg=messagechain_builder(
            text=majsoul.getalltags(event.group.id, target=target, searchtype=searchtype)))


@bot.on(FriendMessage)
async def freshqhpaipu(event: FriendMessage):
    """手动刷新数据库"""
    if event.sender.id == master:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}freshqhdb\s*$", msg.strip())
        if m:
            print("牌谱刷新中")
            await messagechain_sender(msg="牌谱刷新中", event=event)
            await asyqh_autopaipu()


@bot.on(GroupMessage)
async def guan_wang(event: GroupMessage):
    """返回天凤 / 雀魂的游戏网站"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"(雀魂|天凤)官网", msg.strip())
    if m:
        if m.group(1) == '雀魂':
            await bot.send(event, "https://game.maj-soul.net/1/")
        elif m.group(1) == '天凤':
            await bot.send(event, 'https://tenhou.net/')
    return


async def asyqh_autopaipu():
    """结合scheduler自定定时刷新数据库"""
    print("开始查询雀魂信息")
    result = await majsoul.asygetqhpaipu()
    for msgobj in result:
        for group in msgobj['groups']:
            b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
            # await bot.send_group_message(group, msgobj['msg'])
            await messagechain_sender(grouptarget=group, msg=messagechain_builder(imgbase64=b64))
    print(
        f"雀魂自动查询结束,当前时间:{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}")
    return


if qhsettings.get('autoquery', False):
    _searchfrequency = int(qhsettings.get("searchfrequency", 6))
    if int(_searchfrequency) < 1:
        print('查询频率不能为0,将自动设置为6')
        _searchfrequency = 6
    scheduler.add_job(asyqh_autopaipu, 'cron', hour='*', minute=f'0/{_searchfrequency}')
    print(f' |---已添加定时任务 "雀魂自动查询",查询周期{_searchfrequency}分钟')
