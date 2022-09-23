import os

from core.help import add_help
from plugin.ImgGenerator.bwimg import *
from plugin.ImgGenerator.csgokill import *
from plugin.ImgGenerator.groupmember_imgoperation import *

if not os.path.exists('./images/ImgGenerator'):
    os.mkdir(f'./images/ImgGenerator')
if os.path.exists(r'./main.exe'):
    from plugin.ImgGenerator.KissKiss import *
    from plugin.ImgGenerator.jupai import *
    from plugin.ImgGenerator.prank_on_groupmember import *
else:
    _plugins = os.listdir(r'./plugin/ImgGenerator')
    for path in _plugins:
        if os.path.isdir(f'./plugin/ImgGenerator/{path}'):
            if os.path.exists(f'./plugin/ImgGenerator/{path}/__init__.py'):
                exec(f'from plugin.ImgGenerator.{path} import *')


add_help('group', [
    "举牌 [<文本>] :将文本写在举牌小人上发出来，最多40字\n",
    "亲 / 亲亲   @群友 : 两人互亲\n",
    "逮捕(我自己) @群友 : 逮捕某人\n",
    "(我是)小可爱 @群友 : 可爱群友\n",
    "丢/举(我自己)@群友 : 把群友丢出去/举起来\n ",
    "吃掉        @群友 : 把群友吃了\n",
    "bw [<文本>] [<图片>] : 返回一张黑白处理后的图片，底部有一行文字\n",
    "截图  <回复消息> : 将一条文本聊天记录截图\n",
    "击杀[<文本> 或 @群友] : 击杀群友\n"
])
