import re

from mirai import GroupMessage, Plain, FriendMessage, Voice
from core import config, bot, commandpre, commands_map
from plugin.TencentCloudAPI.text_to_voice import VoiceCreater
from utils.MessageChainBuilder import messagechain_builder

__all__ = []
vc = None
master = config.get('master')
_voice_enable = config.get('settings', dict()).get('voice', False)
_TencentCloudConfig = config.get('voicesetting', None)

if _voice_enable:
    vc = VoiceCreater(setting=_TencentCloudConfig)
    __all__.extend(['send_group_voice', 'send_voice_to_group'])


def getbase64voice(text):
    voice = dict(error=False, file=None, errmsg=None)
    if vc:
        voice['file'] = vc.getbase64voice(text=text)
    else:
        voice['error'] = True
    return voice


@bot.on(GroupMessage)
async def send_group_voice(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['sendvoice']['sendvoice']}", msg.strip())
    if m:
        if _voice_enable:
            if _TencentCloudConfig['private']:
                if event.sender.id != master:
                    return
            text = m.group(1).strip()
            if len(text) > 40:
                return await bot.send(event, messagechain_builder(text="文本太长啦", rndimg=True))
            voice = getbase64voice(text)
            if not voice['error']:
                return await bot.send(event, Voice(base64=voice['file']))
                # return await bot.send(event, await Voice.from_local(content=voice['file']))  # 有问题
                # return await bot.send(event, await Voice.from_local(filename=f'./data/audio/{text}.{vc.codec}'))


@bot.on(FriendMessage)
async def send_voice_to_group(event: FriendMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(fr"^{commandpre}{commands_map['sendvoice']['sendgroupvoice']}", msg.strip())
    if m:
        if _voice_enable:
            if _TencentCloudConfig['private']:
                if event.sender.id != master:
                    return
            groupid = int(m.group(1))
            text = m.group(2).strip()
            if len(text) > 40:
                return await bot.send(event, messagechain_builder(text="文本太长啦", rndimg=True))
            voice = getbase64voice(text)
            if not voice['error']:
                return await bot.send_group_message(groupid, Voice(base64=voice['file']))
                # return await bot.send(event, await Voice.from_local(content=voice['file']))  # 有问题
                # return await bot.send(event, await Voice.from_local(filename=f'./data/audio/{text}.{vc.codec}'))

print(f' |---已启用的腾讯云API服务{__all__}')
