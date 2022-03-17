from mirai import WebSocketAdapter
from mirai.bot import Mirai


def create_bot(config):
    return Mirai(
        qq=config['botconfig']['qq'],  # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key=config['adapter']['verify_key'], host=config['adapter']['host'], port=config['adapter']['port']
        )
    )