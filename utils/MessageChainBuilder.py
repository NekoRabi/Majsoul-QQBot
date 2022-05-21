from mirai.models import MessageChain, Plain, Voice, Image,At,AtAll


def buildmessagechain(text=None, imgpath=None, at: int = None, atall=False,voice=None):
    msglist = []
    if at:
        msglist.append(At(at))
        msglist.append(Plain(" "))
    elif atall:
        msglist.append(AtAll())
        msglist.append(Plain(" "))
    if text:
        msglist.append(Plain(text))
    if imgpath:
        msglist.append(Plain("\n"))
        msglist.append(Image(path=imgpath))
    if len(msglist) > 0:
        msgC = MessageChain(msglist)
        return msgC
    else:
        return None
