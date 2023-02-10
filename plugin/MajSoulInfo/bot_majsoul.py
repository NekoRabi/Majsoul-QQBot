"""
:Author:  NekoRabi
:Create:  2022/8/16 16:47
:Update: /
:Describe: 负责雀魂功能与机器人的交互
:Version: 0.6.1
"""
import asyncio
import datetime
import re

from mirai import GroupMessage, Plain, FriendMessage
from mirai.bot import Startup

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
           'freshqhpaipu', 'game_guan_wang', 'qhbind', 'qhbind_operation', 'get_player_detail_website', 'qhgroupauthentication']
_admin = config.get('admin', [])
_master = config.get('master', 1215791340)

_qhsettings = read_file(r'./config/MajSoulInfo/config.yml')

_qhcmd = read_file(r'./config/MajSoulInfo/command.yml')

_blacklist = config.get('blacklist', [])


@bot.on(GroupMessage)
async def disableqhplugin(event: GroupMessage):
    """禁用雀魂指令 """
    if is_having_admin_permission(event) or event.sender.id in _admin:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{_qhcmd['disable']}", msg.strip())
        if m:
            commandname = m.group(2)
            group = event.group.id
            if commandname in ['qhpt', '雀魂分数', '雀魂pt']:
                if group not in _qhsettings['disptgroup']:
                    _qhsettings['disptgroup'].append(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'查分功能禁用成功')
            elif commandname in ['qhpaipu', '雀魂最近对局']:
                if group not in _qhsettings['dispaipugroup']:
                    _qhsettings['dispaipugroup'].append(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'牌谱查询功能禁用成功')
            elif commandname in ['qhinfo', '雀魂玩家详情']:
                if group not in _qhsettings['disinfogroup']:
                    _qhsettings['disinfogroup'].append(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'雀魂玩家详情功能禁用成功')
            elif commandname in ['qhsl', '雀魂十连']:
                if group not in _qhsettings['disslgroup']:
                    _qhsettings['disslgroup'].append(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'模拟十连功能禁用成功')
            elif commandname in ['qhyb', '雀魂月报']:
                if group not in _qhsettings['dispaipugroup']:
                    _qhsettings['dispaipugroup'].append(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'牌谱查询功能禁用成功')
            else:
                return await messagechain_sender(event=event, msg='无此功能,请重新输入参数')


@bot.on(GroupMessage)
async def enableqhplugin(event: GroupMessage):
    """启用雀魂指令"""
    if is_having_admin_permission(event) or event.sender.id in _admin:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(fr"^{commandpre}{_qhcmd['enable']}", msg.strip())
        if m:
            commandname = m.group(2)
            group = event.group.id
            if commandname in ['qhpt', '雀魂分数', '雀魂pt']:
                if group in _qhsettings['disptgroup']:
                    _qhsettings['disptgroup'].remove(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'查分功能启用成功')
            elif commandname in ['qhpaipu', '雀魂最近对局']:
                if group in _qhsettings['dispaipugroup']:
                    _qhsettings['dispaipugroup'].remove(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'牌谱查询功能启用成功')
            elif commandname in ['qhinfo', '雀魂玩家详情']:
                if group in _qhsettings['disinfogroup']:
                    _qhsettings['disinfogroup'].remove(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'雀魂玩家详情功能启用成功')
            elif commandname in ['qhsl', '雀魂十连']:
                if group in _qhsettings['disslgroup']:
                    _qhsettings['disslgroup'].remove(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'模拟十连功能启用成功')
            elif commandname in ['qhyb', '雀魂月报']:
                if group in _qhsettings['dispaipugroup']:
                    _qhsettings['dispaipugroup'].remove(group)
                    write_file(content=_qhsettings, path=r'./config/MajSoulInfo/config.yml')
                    return await messagechain_sender(event=event, msg=f'牌谱查询功能启用成功')
            else:
                return await messagechain_sender(event=event, msg='无此功能,请重新输入参数')


@bot.on(GroupMessage)
async def qhpt(event: GroupMessage):
    """查分"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhpt']}", msg.strip())
    if m:
        if _qhsettings['qhpt'] and event.group.id not in _qhsettings['disptgroup']:

            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhpt')):
                return messagechain_sender(event=event,
                                           msg=await messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True,
                                                                          at=event.sender.id))
            if m.group(3):
                selecttype = int(m.group(3))
                selectindex = m.group(4)
                result = await majsoul.getcertaininfo(m.group(2), selecttype, selectindex)
            else:
                result = await majsoul.query(m.group(2))
            await messagechain_sender(event=event, msg=result)
            # if result['error']:
            #     # await messagechain_sender(event=event, result['msg'])
            #     await sendMsgChain(msg=result['msg'], event=event)
            # else:
            #     await sendMsgChain(msg=await messagechain_builder(imgpath=f'./images/MajsoulInfo/qhpt{m.group(2)}.png'),
            #                        event=event,
            #                        errortext=result['msg'])
            # await messagechain_sender(event=event, imgpath=f'./images/MajsoulInfo/qhpt{m.group(2)}.png'))
        return


@bot.on(GroupMessage)
async def getrecentqhpaipu(event: GroupMessage):
    """查最近牌谱"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhpaipu']}", msg.strip())
    if m:
        if _qhsettings['qhpaipu'] and event.group.id not in _qhsettings['dispaipugroup']:

            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhpaipu')):
                return messagechain_sender(event=event,
                                           msg=await messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True,
                                                                          at=event.sender.id))
            playername = m.group(2)
            searchtype = m.group(3)
            searchnumber = m.group(4)
            result = await majsoul.getsomeqhpaipu(playername=playername, seatchtype=searchtype, counts=searchnumber)
            await messagechain_sender(event=event, msg=result)


@bot.on(GroupMessage)
async def getplayerdetails(event: GroupMessage):
    """查玩家详情"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhinfo']}", msg.strip())
    if m:
        if _qhsettings['qhinfo'] and event.group.id not in _qhsettings['disinfogroup']:

            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhinfo')):
                return messagechain_sender(event=event,
                                           msg=await messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True,
                                                                          at=event.sender.id))
            playername = m.group(2)
            selecttype = m.group(3)
            model = m.group(4)
            selectlevel = m.group(5)
            if selectlevel:
                pass
            else:
                selectlevel = 'all'
            detail = await majsoul.getplayerdetail(
                playername=playername, selecttype=selecttype, model=model, selectlevel=selectlevel)
            await messagechain_sender(event=event, msg=detail)
            # if detail['error']:
            #     await messagechain_sender(event=event, detail['msg'])
            # else:
            #     res = await messagechain_sender(event=event,
            #                          await messagechain_builder(imgpath=f'./images/MajsoulInfo/detail{playername}.png'))
            #     if res == -1:
            #         await messagechain_sender(event=event, detail['msg'])
    return


@bot.on(GroupMessage)
async def getqhmonthreport(event: GroupMessage):
    """查月报"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhyb']}", msg.strip())
    if m:
        if _qhsettings['qhyb'] and event.group.id not in _qhsettings['disybgroup']:
            if not cmdbuffer.updategroupcache(GroupCommand(event.group.id, event.sender.id, 'qhyb')):
                return messagechain_sender(event=event,
                                           msg=await messagechain_builder(text="你查的太频繁了,休息一下好不好", rndimg=True,
                                                                          at=event.sender.id))
            playername = m.group(2)
            selecttype = m.group(3)
            year = m.group(4)
            month = m.group(5)
            report = await majsoul.getmonthreport(
                playername=playername, selecttype=selecttype, year=year, month=month)
            await messagechain_sender(event=event, msg=report)
            # if report['error']:
            #     await messagechain_sender(event=event, report['msg'])
            # else:
            #     res_id = await messagechain_sender(event=event,
            #                             await messagechain_builder(imgpath=f'./images/MajsoulInfo/yb{playername}.png'))
            #     if res_id == -1:
            #         print(f"图片yb{playername}.png发送失败，尝试发送文本")
            #         await messagechain_sender(event=event, report['msg'])
            # await messagechain_sender(event=event,await messagechain_builder()(imgbase64=report['imgbase64']))
    return


@bot.on(GroupMessage)
async def getqhwatcher(event: GroupMessage):
    """获取雀魂订阅"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['getwatch']}", msg.strip())
    if m:
        await messagechain_sender(event=event, msg=majsoul.getallwatcher(event.group.id))


@bot.on(GroupMessage)
async def addmajsoulwatch(event: GroupMessage):
    """加入订阅"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['addwatch']}", msg.strip())
    if m:
        if event.group.id:
            # if is_havingadmin(event):
            #     await messagechain_sender(event=event, addwatch(m.group(2), event.group.id))
            # else:
            #     await messagechain_sender(event=event, await messagechain_builder(at=event.sender.id), text=" 抱歉，只有管理员才能这么做哦")]))
            await messagechain_sender(event=event, msg=majsoul.addwatch(m.group(2), event.group.id,
                                                                        is_having_admin_permission(event)))


@bot.on(GroupMessage)
async def delmajsoulwatch(event: GroupMessage):
    """删除订阅"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['delwatch']}", msg.strip())
    if m:
        if event.group.id:
            # if is_havingadmin(event):
            #     await messagechain_sender(event=event,
            #                    removewatch(playername=m.group(2), groupid=event.group.id))
            # else:
            #     await messagechain_sender(event=event, await messagechain_builder(at=event.sender.id), text=" 抱歉，只有管理员才能这么做哦")]))
            await messagechain_sender(event=event, msg=majsoul.removewatch(m.group(2), event.group.id,
                                                                           is_having_admin_permission(event)))
    return


@bot.on(GroupMessage)
async def qhdrawcards(event: GroupMessage):
    """雀魂十连抽卡模拟"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['qhsl']}", msg.strip())
    if m:
        if _qhsettings['qhsl'] and event.group.id not in _qhsettings['disslgroup']:
            if event.sender.id in _blacklist:
                return await messagechain_sender(event=event,
                                                 msg=await messagechain_builder(text='你已被列入黑名单', at=event.sender.id))
            if m.group(2):
                if m.group(2) in ['限时', '限定', 'up', 'UP']:
                    result = majsoul.drawcards(userid=event.sender.id, up=True)
                    if result['error']:
                        return await messagechain_sender(event=event,
                                                         msg=await messagechain_builder(at=event.sender.id,
                                                                                        text=result['resultsmsg']))
                    # mergeimgs(result.get('results'), event.sender.id)
                    # await messagechain_sender(event=event, await messagechain_builder(
                    #     at=event.sender.id,
                    #     text="抽卡结果:", imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
                    # return await messagechain_sender(event=event, await messagechain_builder(
                    #     at=event.sender.id),
                    #     text=result['resultsmsg'])
                    # ]))
                    await messagechain_sender(event=event,
                                              msg=await messagechain_builder(at=event.sender.id, text='抽卡结果',
                                                                             imgbase64=mergeimgs(
                                                                                 result.get('results'))))
                elif m.group(2) in ['常驻', '普通', 'common', 'normal']:
                    result = majsoul.drawcards(userid=event.sender.id, up=False)
                    if result['error']:
                        return await messagechain_sender(event=event,
                                                         msg=await messagechain_builder(at=event.sender.id,
                                                                                        text=result['resultsmsg']))
                    # mergeimgs(result.get('results'), event.sender.id)
                    # await messagechain_sender(event=event, await messagechain_builder(
                    #     at=event.sender.id,
                    #     text="抽卡结果:",
                    #     imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
                    # return await messagechain_sender(event=event, await messagechain_builder(
                    #     at=event.sender.id),
                    #     text=result['resultsmsg'])
                    # ]))
                    await messagechain_sender(event=event,
                                              msg=await messagechain_builder(at=event.sender.id, text='抽卡结果',
                                                                             imgbase64=mergeimgs(
                                                                                 result.get('results'))))
                else:
                    result = majsoul.drawcards(userid=event.sender.id, up=False)
                    if result['error']:
                        return await messagechain_sender(event=event,
                                                         msg=await messagechain_builder(at=event.sender.id,
                                                                                        text=result['resultsmsg']))
                    await messagechain_sender(event=event,
                                              msg=await messagechain_builder(at=event.sender.id,
                                                                             text='参数输入有误，请输入“限时”或“常驻”，此次十连将输出常驻'))
                    # mergeimgs(
                    #     result.get('results'), event.sender.id)
                    # await messagechain_sender(event=event, await messagechain_builder(
                    #     at=event.sender.id,
                    #     text="抽卡结果:",
                    #     imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
                    # return await messagechain_sender(event=event, await messagechain_builder(
                    #     at=event.sender.id),
                    #     text=result['resultsmsg'])
                    # ]))
                    await messagechain_sender(event=event,
                                              msg=await messagechain_builder(at=event.sender.id, text='抽卡结果',
                                                                             imgbase64=mergeimgs(
                                                                                 result.get('results'))))
            else:
                result = majsoul.drawcards(userid=event.sender.id, up=False)
                if result['error']:
                    return await messagechain_sender(event=event,
                                                     msg=await messagechain_builder(at=event.sender.id,
                                                                                    text=result['resultsmsg']))
                # mergeimgs(
                #     result.get('results'), event.sender.id)
                # await messagechain_sender(event=event, await messagechain_builder(
                #     at=event.sender.id,
                #     text="抽卡结果:",
                #     imgpath=f"./images/MajSoulInfo/{event.sender.id}.png"))
                await messagechain_sender(event=event, msg=await messagechain_builder(at=event.sender.id, text='抽卡结果',
                                                                                      imgbase64=mergeimgs(
                                                                                          result.get('results'))))
        else:
            return await messagechain_sender(event=event, msg=await messagechain_builder(text="此群已禁用模拟抽卡"))
    return


@bot.on(GroupMessage)
async def getmyqhdrawcards(event: GroupMessage):
    """获取抽卡记录"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['getmyqhsl']}", msg.strip())
    if event.sender.id in _blacklist:
        return
    if m:
        return await messagechain_sender(event=event, msg=majsoul.getmycard(event.sender.id))


@bot.on(GroupMessage)
async def clearmajsoulwatcher(event: GroupMessage):
    """清空x群的雀魂订阅"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['clearwatch']}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            await messagechain_sender(event=event, msg=majsoul.clearallwatch(groupid=event.group.id))
        else:
            await messagechain_sender(event=event,
                                      msg=await messagechain_builder(at=event.sender.id, text=" 抱歉，只有管理员才能这么做哦"))


@bot.on(GroupMessage)
async def qhaddtag(event: GroupMessage):
    """为x群的雀魂玩家添加昵称或者是Tag"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['tagon']}", msg.strip())
    if m:
        if not m.group(3):
            return await messagechain_sender(event=event, msg=await messagechain_builder(text='请输入你要添加tag哦'))
        if is_having_admin_permission(event):
            await messagechain_sender(event=event,
                                      msg=majsoul.tagonplayer(playername=m.group(2), tagname=m.group(3),
                                                              userid=event.sender.id,
                                                              groupid=event.group.id))
        else:
            await messagechain_sender(event=event,
                                      msg=await messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))


@bot.on(GroupMessage)
async def qhdeltag(event: GroupMessage):
    """删除昵称或者Tag"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['tagoff']}", msg.strip())
    if m:
        if is_having_admin_permission(event):
            tagnames = None
            if m.group(3):
                tagnames = m.group(3)
            await messagechain_sender(event=event,
                                      msg=majsoul.tagoffplayer(playername=m.group(2), groupid=event.group.id,
                                                               userid=event.sender.id, tagname=tagnames))
        else:
            await messagechain_sender(event=event,
                                      msg=await messagechain_builder(at=event.sender.id, text='抱歉，只有管理员才能这么做'))


@bot.on(GroupMessage)
async def qhtagoperate(event: GroupMessage):
    """tag批量操作"""
    if event.sender.id in _blacklist:
        return
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
            await messagechain_sender(await messagechain_builder(text=result), event)


@bot.on(GroupMessage)
async def qhlisttag(event: GroupMessage):
    """获取所有Tag"""
    if event.sender.id in _blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{_qhcmd['taglist']}", msg.strip())
    if m:
        target = m.group(2)
        searchtype = 'playername'
        if target:
            if target.startswith('tag=') or target.startswith('tagname='):
                target = target.split('=', 2)[1]
                searchtype = 'tagname'
        await messagechain_sender(event=event, msg=await messagechain_builder(
            text=majsoul.getalltags(event.group.id, target=target, searchtype=searchtype)))


@bot.on(FriendMessage)
async def freshqhpaipu(event: FriendMessage):
    """机器人主人手动刷新数据库"""
    if event.sender.id == _master:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{_qhcmd.get('dbupdate', 'qhfreshdb$')}", msg.strip())
        if m:
            print("牌谱刷新中")
            await messagechain_sender(msg="牌谱数据库刷新中", event=event)
            await asyqh_autopaipu()
            await messagechain_sender(msg="牌谱刷新完成", event=event)


@bot.on(FriendMessage)
async def changenode(event: FriendMessage):
    """机器人主人手动刷新链路"""
    if event.sender.id == _master:
        msg = "".join(map(str, event.message_chain[Plain]))
        m = re.match(
            fr"^{commandpre}{_qhcmd.get('changlinke', 'qhfreshlink$')}", msg.strip())
        if m:
            print("牌谱刷新中")
            await messagechain_sender(msg="自动选择牌谱屋链路中", event=event)
            await majsoul.set_link_node()
            await messagechain_sender(msg=f"自动切换至链路{await majsoul.set_link_node()}", event=event)


@bot.on(GroupMessage)
async def qhbind(event: GroupMessage):
    """账号绑定"""
    msg = "".join(map(str, event.message_chain[Plain]))
    defaultcmd = r'(qhbind|雀魂绑定)\s*(\S+)$'
    m = re.match(fr"^{commandpre}{_qhcmd.get('qhbind', defaultcmd)}", msg.strip())
    if m:
        playernamme = m.group(2)
        await messagechain_sender(event=event, msg=await majsoul.bind_account(event.sender.id, playernamme))
    return


@bot.on(GroupMessage)
async def qhbind_operation(event: GroupMessage):
    """绑定账号可用的操作"""
    msg = "".join(map(str, event.message_chain[Plain]))
    defaultcmd = r'qhm(pt|yb|info|paipu)\s*([34])?\s*(\S+|\d{4}-\d{1,2})?$'
    m = re.match(
        fr"^{commandpre}{_qhcmd.get('qhm_operation', defaultcmd)}", msg.strip())
    if m:
        operation = m.group(1)
        search_type = m.group(2)
        other = m.group(3)
        await messagechain_sender(event=event, msg=await majsoul.bind_operation(qq=event.sender.id, opertaion=operation,
                                                                                searchtype=search_type, other=other))
    return


@bot.on(GroupMessage)
async def qhgroupauthentication(event: GroupMessage):
    """雀魂群组权限控制"""
    msg = "".join(map(str, event.message_chain[Plain]))
    defaultcmd = r'qhauthority\s*(\w+)\s*$'
    m = re.match(
        fr"^{commandpre}{_qhcmd.get('qhauthority', defaultcmd)}", msg.strip())
    if m:
        if not is_having_admin_permission(event=event):
            return await messagechain_sender(event=event, msg=await messagechain_builder(text='抱歉, 只有管理员有权限这么做'))
        enable = m.group(1).lower()

        if enable in ['enable', 'true', 'open']:
            enable = True
        elif enable in ['disable', 'false', 'cross', 'close']:
            enable = False
        else:
            return await messagechain_sender(event=event, msg=await messagechain_builder(text='指令有误'))

        await messagechain_sender(event=event, msg=await majsoul.authentication_controller(event.group.id, enable))
    return


@bot.on(GroupMessage)
async def game_guan_wang(event: GroupMessage):
    """返回天凤 / 雀魂的游戏网站"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"(雀魂|天凤)官网", msg.strip())
    if m:
        if m.group(1) == '雀魂':
            await messagechain_sender(event=event, msg="https://game.maj-soul.net/1/")
        elif m.group(1) == '天凤':
            await messagechain_sender(event=event, msg='https://tenhou.net/')
    return


@bot.on(GroupMessage)
async def get_player_detail_website(event: GroupMessage):
    """返回天凤 / 雀魂的游戏数据查询网站"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"(雀魂|天凤)(牌谱屋|水表网)", msg.strip())
    if m:
        if m.group(1) == '雀魂':
            await messagechain_sender(event=event, msg="https://amae-koromo.sapk.ch/")
        elif m.group(1) == '天凤':
            await messagechain_sender(event=event, msg='https://nodocchi.moe/tenhoulog/')
    if msg.strip().lower() == "mortal":
        await messagechain_sender(event=event,msg='https://mjai.ekyu.moe')
    return


@bot.on(Startup)
async def linksetting(_):
    """机器人开机时自动选择结点"""
    await majsoul.set_link_node()


async def asyqh_autopaipu():
    """结合scheduler自定定时刷新数据库"""
    if not _qhsettings.get('silence_CLI', False):
        print("开始查询雀魂信息")
    result = await majsoul.asygetqhpaipu()
    if len(result) > 0:
        print(f'新的雀魂结算:{result}')
        index = 0
        _broadcast_type = _qhsettings.get('broadcast', 'image').lower()
        if _broadcast_type in ['txt', 'text', 'str']:
            for msgobj in result:
                for group in msgobj['groups']:
                    index += 1
                    if index % 10 == 0:
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(0.005)
                    await messagechain_sender(grouptarget=group, msg=await messagechain_builder(text=msgobj['msg']))
        elif _broadcast_type in ['mix', 'mixed']:
            for msgobj in result:
                for group in msgobj['groups']:
                    index += 1
                    if index % 10 == 0:
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(0.005)
                    b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
                    await messagechain_sender(grouptarget=group,
                                              msg=await messagechain_builder(text=msgobj['link'], imgbase64=b64))
        else:
            for msgobj in result:
                for group in msgobj['groups']:
                    index += 1
                    if index % 10 == 0:
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(0.005)
                    b64 = text_to_image(text=msgobj['msg'], needtobase64=True)
                    # await messagechain_sender_group_message(group, msgobj['msg'])
                    await messagechain_sender(grouptarget=group, msg=await messagechain_builder(imgbase64=b64))
    if not _qhsettings.get('silence_CLI', False):
        print(
            f"雀魂自动查询结束,当前时间:{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}")
    return


if _qhsettings.get('autoquery', False):
    _searchfrequency = int(_qhsettings.get("searchfrequency", 6))
    if int(_searchfrequency) < 1 or int(_searchfrequency) > 29:
        print('查询频率有误,将自动设置为6')
        _searchfrequency = 6
    scheduler.add_job(asyqh_autopaipu, 'cron', minute=f'0/{_searchfrequency}')
    print(f' |---已添加定时任务 "雀魂自动查询",查询周期{_searchfrequency}分钟')
if _qhsettings.get('link_update', True):
    link_freshtime: str = _qhsettings.get('link_freshtime', '2:33')
    scheduler.add_job(majsoul.set_link_node, 'cron', hour=f'{link_freshtime.split(":")[0]}',
                      minute=f'{link_freshtime.split(":")[1]}')
    print(f' |---已添加定时任务 "定时刷新牌谱屋结点",将在每天{link_freshtime}执行')
