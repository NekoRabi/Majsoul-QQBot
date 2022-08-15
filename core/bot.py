from mirai import Mirai, WebSocketAdapter
from utils.cfg_loader import loadcfg_from_file

bot_cfg = loadcfg_from_file(r'./config/config.yml')
bot_cfg = dict(adapter=bot_cfg.get('adapter'), id=int(bot_cfg['botconfig']['qq']),
               nickname=bot_cfg['botconfig'].get('botname', ''))

bot = Mirai(
    qq=bot_cfg.get('id'),  # 改成你的机器人的 QQ 号
    adapter=WebSocketAdapter(
        verify_key=bot_cfg['adapter']['verify_key'], host=bot_cfg['adapter']['host'], port=bot_cfg['adapter']['port']
    )
)
