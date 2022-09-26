"""
:Author:  NekoRabi
:Create:  2022/9/23 14:07
:Update: /
:Describe: 生成CSGO的击杀图片
:Version: 0.0.1
"""
import base64
import random
import re
import os
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from mirai import GroupMessage, Plain, At
from core import bot, blacklist
from utils.MessageChainBuilder import messagechain_builder

__all__ = ['cskill']


async def jisha(user: str, target: str, headshot=None, penetrate=None):
    """
    user: 击杀人
    target: 击杀目标
    击杀图片生成消息链
    """
    gun_file = random.choice(os.listdir(f'./plugin/ImgGenerator/image/cs/')).replace('.png', '')
    while gun_file in ['headshot', 'penetrate']:
        gun_file = random.choice(os.listdir(f'./plugin/ImgGenerator/image/cs/')).replace('.png', '')
    # gun_file = random.choice(['ak47', 'awp', 'knife', 'm4a1', 'p90', 'deagle', 'fn57', 'hegrenade', 'usp'])
    gun = f'./plugin/ImgGenerator/image/cs/{gun_file}.png'
    font = ImageFont.truetype('./plugin/ImgGenerator/MiSans-Bold.ttf', 30)
    headshot = random.random()
    headshot_img = None
    himg_a = None
    penetrate = random.random()
    penetrate_img = None
    pimg_a = None
    if gun_file not in ['hegrenade', 'defuser', 'flashbang', 'diversion', 'fists', 'inferno', 'headshot', 'penetrate']:
        if not gun_file.startswith('knife'):
            if headshot < 0.1:
                headshot_img = Image.open(f'./plugin/ImgGenerator/image/cs/headshot.png')
            if penetrate < 0.1:
                penetrate_img = Image.open(f'./plugin/ImgGenerator/image/cs/penetrate.png')
    width, height = font.getsize(user)
    width2, height2 = font.getsize(target)
    img_gun = Image.open(gun)
    width_gun, height_gun = img_gun.size
    g_a = img_gun.split()[3]  # 获取 A通道 信息

    # 开始定位
    total_width = width + width2 + width_gun + 30
    gun_posx = width + 10
    killed_posx = width + width_gun + 18

    if headshot_img:
        total_width += headshot_img.size[0]
        killed_posx += headshot_img.size[0]
        himg_a = headshot_img.split()[3]
    if penetrate_img:
        total_width += penetrate_img.size[0]
        killed_posx += penetrate_img.size[0]
        pimg_a = penetrate_img.split()[3]

    img = Image.new('RGBA', (total_width, 50), (255, 0, 0))
    img_bg = Image.new('RGBA', (total_width - 10, 42), (0, 0, 0, 112))
    img.paste(img_bg, (6, 4))
    img.paste(img_gun, (gun_posx, 10), g_a)
    if penetrate_img:
        img.paste(penetrate_img, (gun_posx + width_gun, 10), pimg_a)
    if headshot_img:
        if penetrate_img:
            img.paste(headshot_img, (gun_posx + width_gun + penetrate_img.size[0], 10), himg_a)
        else:
            img.paste(headshot_img, (gun_posx + width_gun, 10), himg_a)
    draw = ImageDraw.Draw(img)
    draw.text((8, 2), user, font=font, fill='#eabe54')
    draw.text((killed_posx, 2), target,
              font=font, fill='#6f9ce6')
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return await messagechain_builder(imgbase64=base64_str)


@bot.on(GroupMessage)
async def cskill(event: GroupMessage):
    if event.sender.id in blacklist:
        return
    msg = "".join(map(str, event.message_chain[Plain]))
    m = re.match(
        fr"^击杀(\S+)?$", msg.strip())
    if m:
        if m.group(1):
            await bot.send(event, await jisha(event.sender.member_name, m.group(1)))
        elif At in event.message_chain:
            target_id = event.message_chain.get_first(At).target
            memberinfo = await bot.get_group_member(group=event.group.id, id_=target_id)
            if not memberinfo:
                memberprofile = await bot.member_profile.get(target=event.group.id, member_id=target_id)
                membername = memberprofile.nickname
            else:
                membername = memberinfo.member_name
            await bot.send(event, await jisha(event.sender.member_name, membername))
