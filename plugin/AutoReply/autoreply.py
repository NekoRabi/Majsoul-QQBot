"""
:Author:  NekoRabi
:Update Time:  2022/8/16 16:15
:Describe: 随即消息回复
:Version: 0.0.2
"""
import random
import re

from mirai import GroupMessage, Plain

from core import bot, bot_cfg, config, commandpre, commands_map, replydata
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import sendMsgChain
from utils.cfg_loader import w_cfg_to_file

settings = config.get('settings')
whitelist = config['whitelist']
alarmclockgroup = config['alarmclockgroup']
silencegroup = config['silencegroup']
repeatconfig = config['repeatconfig']
norepeatgroup = config['norepeatgroup']
qhsettings = config['qhsettings']
botname = bot_cfg.get('nickname', '')
admin = config['admin']
black_list = dict(user=config['blacklist'], group=config['mutegrouplist'])

__all__ = ['duideduide','randominterrupt','diyreply','config_group_repeat']


@bot.on(GroupMessage)
async def duideduide(event: GroupMessage):
    if not settings['silence']:
        if event.group.id not in silencegroup:
            if len(event.message_chain[Plain]) == 1:
                msg = str(event.message_chain[Plain][0]).strip()

                if msg in ['正确的', '直接的', '中肯的', '雅致的', '客观的', '整体的', '立体的', '全面的', '辩证的', '形而上学的', '雅俗共赏的', '一针见血的',
                           '直击要害的', '错误的', '间接的', '虚伪的', '庸俗的', '主观的', '平面的', '片面的', '孤立的', '辩证法的', '雅俗之分',
                           '的离题万里的',
                           '不痛不痒的']:
                    if random.random() < 0.3:
                        await bot.send(event, random.choice(
                            ['正确的', '直接的', '中肯的', '雅致的', '客观的', '整体的', '立体的', '全面的', '辩证的', '形而上学的', '雅俗共赏的',
                             '一针见血的',
                             '直击要害的', '错误的', '间接的', '虚伪的', '庸俗的', '主观的', '平面的', '片面的', '孤立的', '辩证法的', '雅俗之分的',
                             '离题万里的',
                             '不痛不痒的']))
                # 方舟肉鸽词库
                elif msg in ['迷茫的', '盲目的', '孤独的', '生存的', '臆想的', '谨慎的', '暴怒的', '偏执的', '敏感的']:
                    if random.random() < 0.3:
                        await bot.send(event, random.choice(
                            ['正确的', '错误的', '辩证的', '迷茫的', '盲目的', '孤独的', '生存的', '臆想的', '谨慎的', '暴怒的', '偏执的', '敏感的']))

                elif msg in ['典', '孝', '麻', '盒', '急', '蚌', '赢', '乐', '创', '绝', '厥', '退', '急了']:
                    if random.random() < 0.3:
                        await sendMsgChain(messagechain_builder(
                            text=random.choice(['典', '孝', '麻', '盒', '急', '蚌', '赢', '乐', '创', '绝', '厥', '退', '急'])),
                            event=event)


@bot.on(GroupMessage)
async def randominterrupt(event: GroupMessage):
    """
    随即打断群友发言或者复读群友
    :param event:
    :return:
    """
    if not (settings['silence'] or settings['norepeat']):
        if event.group.id not in silencegroup:
            if event.group.id not in norepeatgroup:
                count = random.random() * 100
                msg = event.message_chain[Plain]
                senderid = event.sender.id
                if senderid in whitelist:
                    return
                if str(event.message_chain) in ['?', "？"] and count < repeatconfig['repeatQ']:
                    print(f"在{event.group.name}群,复读了一次?")
                    return await bot.send(event, "?")
                if count < repeatconfig['interruptQQ']:
                    print(f"在{event.group.name}群,打断一次{msg}")
                    return await bot.send(event, random.choice(["¿", "?????"]))
                elif count < repeatconfig['interruptQ']:
                    print(f"在{event.group.name}群,打断一次{msg}")
                    return await bot.send(event, "?")
                elif count < repeatconfig['repeatmsg']:
                    print(f"在{event.group.name}群,复读一次{msg}")
                    return await bot.send(event, event.message_chain)
    return


@bot.on(GroupMessage)
async def diyreply(event: GroupMessage):
    """
    消息主体为机器人时，触发自定义回复
    :param event:
    :return:
    """
    if not settings['silence'] and repeatconfig['autoreply']:
        if event.group.id not in silencegroup:
            msg = "".join(map(str, event.message_chain[Plain]))
            m = re.match(fr"^{commandpre}{commands_map['reply']['jida']}", msg.strip())
            if m:
                return await bot.send(event,
                                      f"{m.group(1)}说，他有五个鸡，我说，立直鸡，副露鸡，默听鸡，自摸鸡，放铳鸡\n{m.group(1)}还说，他有四个鸡，我说，坐东鸡，坐西鸡，坐南鸡，坐北鸡\n{m.group(1)}又说，他有三个鸡，我说，上一打鸡，这一打鸡，下一打鸡\n{m.group(1)}又说，他有两个鸡，我说，子家鸡 亲家鸡\n{m.group(1)}最后说，他有一个鸡，我说，{m.group(1)}就是鸡")
            m1 = re.match(fr"^{commandpre}{commands_map['reply']['wochao']}", msg.strip())
            if m1:
                return await bot.send(event,
                                      f"考试中 {event.sender.member_name}想抄{m1.group(1)}的答案🥵{m1.group(1)}一直挡着说 不要抄了 不要抄了🥵当时{m1.group(1)}的眼泪都流下来了🥵可是{event.sender.member_name}还是没听{m1.group(1)}说的🥺一直在抄{m1.group(1)}🥵呜呜呜呜🥺 因为卷子是正反面 说亲自动手 趁监考老师不注意的时候把{m1.group(1)}翻到反面 翻来覆去抄{m1.group(1)}🥵抄完前面抄后面🥵🥵🥵")

            senderid = event.sender.id
            if botname == "":
                return
            if botname in event.message_chain:
                if senderid in black_list['user']:
                    return await bot.send(event, messagechain_builder(reply_choices=replydata['blackuser']))
                msg = msg.replace(f"{botname}", "", 1)
                if settings['r18talk']:
                    if senderid in admin:
                        for k, v in replydata['r18'].items():
                            if k in msg:
                                return await bot.send(event, messagechain_builder(reply_choices=v, rndimg=True))
                        return await bot.send(event,
                                              messagechain_builder(reply_choices=replydata['mismatch']['admin'],
                                                                   rndimg=True))
                    else:
                        for k, v in replydata['common'].items():
                            if k in msg:
                                return await bot.send(event, messagechain_builder(reply_choices=v, rndimg=True))
                        return await bot.send(event,
                                              messagechain_builder(reply_choices=replydata['mismatch']['common'],
                                                                   rndimg=True))
                else:
                    for k, v in replydata['common'].items():
                        if k in msg:
                            return await bot.send(event, messagechain_builder(reply_choices=v, rndimg=True))
                    return await bot.send(event, messagechain_builder(reply_choices=replydata['mismatch']['common'],
                                                                      rndimg=True))


@bot.on(GroupMessage)
async def config_group_repeat(event: GroupMessage):
    """
    关闭自动回复
    :param event:
    :return:
    """
    msg = "".join(map(str, event.message_chain[Plain]))
    userid = event.sender.id
    # 匹配指令
    if userid in admin:
        m = re.match(fr"^{commandpre}{commands_map['sys']['repeat']}", msg.strip())
        if m:
            if m.group(1).lower() in ['on', 'true']:
                print(f'已将{event.group.id}的复读关闭')
                if event.group.id not in norepeatgroup:
                    norepeatgroup.append(event.group.id)
                    w_cfg_to_file(content=config, path=r'./config/config.yml')
            else:
                if event.group.id in norepeatgroup:
                    print(f'已将{event.group.id}的复读开启')
                    norepeatgroup.remove(event.group.id)
                    w_cfg_to_file(content=config, path=r'./config/config.yml')
