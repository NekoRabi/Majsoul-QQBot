import random

from mirai import MessageChain, At, Plain, AtAll, Image

from utils.cfg_loader import loadcfg_from_file

config = loadcfg_from_file(r'./config/config.yml')


def messagechain_builder(reply_choices: list = None, text: str = None, imgpath: str = None, imgurl: str = None, imgbase64=None,
                 at: int = None, atall=False) -> MessageChain:
    msgchain = []
    if at:
        msgchain.append(At(at))
        msgchain.append(Plain(" "))
    elif atall:
        msgchain.append(AtAll())
        msgchain.append(Plain(" "))
    if reply_choices:
        msgchain.append(Plain(random.choice(reply_choices)))
    elif text:
        msgchain.append(Plain(text))
    if reply_choices or text:
        msgchain.append(Plain(' '))
    if imgpath:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(
            Image(path=f"{imgpath}"))
    if imgbase64:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(Image(base64=imgbase64))
    if imgurl:
        if reply_choices or text:
            msgchain.append(Plain("\n"))
        msgchain.append(Image(url=imgurl))
    return MessageChain(msgchain)
