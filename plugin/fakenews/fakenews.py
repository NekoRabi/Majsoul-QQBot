import re

from mirai import GroupMessage, Plain

from core import bot, commandpre, add_help
from utils.MessageChainBuilder import messagechain_builder
from utils.MessageChainSender import messagechain_sender

from mirai import At
from mirai.models import ForwardMessageNode, Forward

__all__ = ['fakenews']

@bot.on(GroupMessage)
async def fakenews(event: GroupMessage):
    """假消息"""
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^{commandpre}\s*fakenews\s*(\S+)\s*$", msg.strip())
    if m:
        if At in event.message_chain:
            at = event.message_chain[At][0].target

            member_profile = await bot.member_profile.get(event.group.id, at)
            memberinfo = await bot.get_group_member(group=event.group.id, id_=at)
            if memberinfo:
                name = memberinfo.member_name
            else:
                name = member_profile.nickname
            fmn = ForwardMessageNode(
                sender_id=at,
                sender_name=name,
                message_chain=await messagechain_builder(
                    text=m.group(1))
            )
            await messagechain_sender(event=event, msg=Forward(node_list=[fmn]))

add_help('group',[
    "fakenews @群友 [文本]: 假消息\n"
])