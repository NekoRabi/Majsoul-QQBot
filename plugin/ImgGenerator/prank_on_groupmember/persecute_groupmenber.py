"""
:Author:  NekoRabi
:Create:  2022/8/13 20:13
:Update: /
:Describe: 一个'迫害'群友的插件
"""
import base64
import re
import aiohttp
import mirai.exceptions
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from mirai.models import Plain, GroupMessage, Quote
from core import bot
from utils.MessageChainBuilder import messagechain_builder

default_fontsize = 48
default_maxwidth = default_fontsize * 15



__all__ = ['groupmessage_screenshot']


async def get_head_sculpture(userid) -> Image:
    """
    获取头像
    :param userid: QQ号。
    :return: 返回QQ头像
    """
    url = f'http://q1.qlogo.cn/g?b=qq&nk={userid}&s=640'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()
    img = Image.open(BytesIO(img_content)).convert("RGBA")
    width = min(img.size)
    img = img.resize((width, width), Image.ANTIALIAS)
    return circle_corner(img, width // 2)


def circle_corner(img, radii=default_fontsize):  # 将矩形圆角化
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """

    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

    # 原图
    img = img.convert("RGBA")
    w, h = img.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img


def addfont(text: str, sender_name=None, position: tuple = (0, 0), textcolor=(0, 0, 0), fontsize=default_fontsize,
            light=False):
    """
    圆角处理
    :param text: 文本内容。
    :param sender_name: 昵称
    :param position: 贴图位置，默认左上角
    :param textcolor: 字体颜色
    :param fontsize: 字体大小
    :param light: 是否亮色模式
    :return:
    """
    line_count = 1  # 总的文本行数
    font = ImageFont.truetype(
        font='./data/fonts/shs_and_emoji.ttf', size=fontsize)  # 打开字体
    # font = ImageFont.truetype(
    #     font='./data/fonts/NotoSansTC-Bold.ttf', size=fontsize)
    allcontent = []
    linetext = []
    textwidth = font.getsize(text)[0]
    nameline = []
    line_heaight = fontsize + 2  # 行高
    temptext0 = ''
    temptext1 = ''

    name_font = ImageFont.truetype(font='./data/fonts/MiSans-Bold.ttf', size=fontsize)
    maxwidth = max(font.getsize(text)[0], font.getsize(sender_name)[0])  # 获取文本的最大宽度
    if sender_name:
        for one_word in sender_name:
            temptext0 += one_word
            if name_font.getsize(temptext0)[0] > default_maxwidth:  # 如果一行文本宽度超过360，进行换行，并将文本最大宽度设置为360
                nameline.append(temptext1)
                temptext0 = one_word
                maxwidth = default_maxwidth
                textwidth = maxwidth
                line_count += 1  # 换行
            temptext1 = temptext0
        if temptext0 != '':  # 如果最后还有剩余，则将整行push
            nameline.append(temptext0)
        temptext0 = ''
        temptext1 = ''
        allcontent.append(nameline)
        line_count += 2
    for one_word in text:
        if one_word == '\n':  # 检测到文本中的 换行，强制进行换行
            linetext.append(temptext1)
            temptext0 = ''
            temptext1 = ''
            line_count += 1
            continue
        temptext0 += one_word
        if font.getsize(temptext1)[0] > default_maxwidth:
            linetext.append(temptext1)
            temptext0 = one_word
            maxwidth = default_maxwidth
            line_count += 1
        temptext1 = temptext0
    if temptext0.strip() != '':
        linetext.append(temptext0)
    allcontent.append(linetext)
    # 生成文字底图，四周留出空白
    if light:
        bgkcolor = '#dddddd'
        namecolor = (32, 32, 192)
        fontbgk_color = (192, 192, 192)
    else:
        bgkcolor = '#141414'
        namecolor = (128, 255, 255)
        fontbgk_color = (45, 45, 45)
    img = Image.new('RGBA', (maxwidth + 2 * fontsize, (line_count + 1) * line_heaight), bgkcolor)
    imgfont = Image.new('RGBA', (textwidth + 2 * fontsize, (len(linetext) + 1) * line_heaight), fontbgk_color)
    draw = ImageDraw.Draw(img)
    drawfont = ImageDraw.Draw(imgfont)
    if len(allcontent) > 1:
        for i in range(len(nameline)):
            # 添加文字
            draw.text((position[0], position[1] + i * line_heaight + 4), text=nameline[i], font=name_font,
                      fill=namecolor)
        for i in range(len(linetext)):
            drawfont.text((position[0] + fontsize, position[1] + i * line_heaight + line_heaight // 2),
                          text=linetext[i],
                          font=font, fill=textcolor)

        imgfont = circle_corner(imgfont, radii=fontsize // 2)
        fontmask = imgfont.split()[3]
        img.paste(imgfont, (position[0], position[1] + len(nameline) * line_heaight + line_heaight // 2),
                  mask=fontmask)
    else:
        for i in range(len(linetext)):
            draw.text((position[0] + fontsize, position[1] + i * line_heaight), text=linetext[i], font=font,
                      fill=textcolor)

        imgfont = circle_corner(imgfont)
        fontmask = imgfont.split()[3]
        img.paste(imgfont, (position[0], position[1]), mask=fontmask)
    img = circle_corner(img, radii=fontsize // 2)
    return maxwidth + 2 * fontsize, (line_count + 1) * line_heaight, img


@bot.on(GroupMessage)
async def groupmessage_screenshot(event: GroupMessage):
    """
    迫害群友
    """
    quote_find_error = False
    msg = "".join(map(str, event.message_chain[Plain]))
    bgkcolor = '#141414'
    textcolor = '#FFFFFF'
    lightmode = False
    m = re.match(
        fr"^截图\s*(\w+)?$", msg.strip())
    if m:
        if Quote in event.message_chain:
            quote = event.message_chain.get_first(Quote)  # 获取回复文本
            message_event_id = quote.id
            try:
                message_event = await bot.message_from_id(message_event_id)
                origin_msg = "".join(map(str, message_event.message_chain[Plain]))
            except mirai.exceptions.ApiError as e:
                # print(f'获取回复消息发送错误{e}')
                quote_find_error = True
                origin_msg = "".join(map(str, quote.origin[Plain]))
            origin_msg = origin_msg.replace('[图片]', '').replace('[动画表情]', '').replace('[符号表情]', '')
            origig_sender = quote.sender_id
            if origin_msg == '':
                return await bot.send(event, messagechain_builder(text='只能截图文本哦'))
            headimg = await get_head_sculpture(origig_sender)
            headimg = headimg.resize((default_fontsize * 5, default_fontsize * 5), Image.ANTIALIAS)
            memberinfo = await bot.get_group_member(group=event.group.id, id_=origig_sender)  # 获取群友群信息
            if m.group(1):
                if m.group(1) in ['light', '白底', '浅色', '亮色', '明亮']:
                    bgkcolor = '#dddddd'
                    lightmode = True
                    textcolor = '#141414'
            if memberinfo:
                text_w, text_h, text_img = addfont(origin_msg, sender_name=memberinfo.member_name, textcolor=textcolor,
                                                   light=lightmode)
            else:
                # 如果群友没有群信息，则尝试获取个人资料
                member_profile = await bot.member_profile.get(event.group.id, origig_sender)
                text_w, text_h, text_img = addfont(origin_msg, sender_name=member_profile.nickname, textcolor=textcolor,
                                                   light=lightmode)
            bgk = Image.new('RGBA',
                            (text_w + default_fontsize * 9, max(text_h + default_fontsize * 2, default_fontsize * 7)),
                            bgkcolor)
            bgk.paste(headimg, (default_fontsize * 20 // 24, default_fontsize * 20 // 24), mask=headimg.split()[3])
            if text_h < 5 * default_fontsize:
                bgk.paste(text_img, (default_fontsize // 24 * 160, default_fontsize // 24 * 80 - text_h // 2),
                          mask=text_img.split()[3])
            else:
                bgk.paste(text_img, (default_fontsize // 24 * 160, default_fontsize // 24 * 20),
                          mask=text_img.split()[3])
            bgk = circle_corner(bgk, radii=default_fontsize * 2)
            # 将图片转换为 base64
            img_bytes = BytesIO()
            bgk.save(img_bytes, format='PNG')
            b_content = img_bytes.getvalue()
            imgcontent = base64.b64encode(b_content)
            # QQ发送消息
            if quote_find_error:
                msgchain = messagechain_builder(text='消息似乎太久了，找不到完整的了', imgbase64=imgcontent)
            else:
                msgchain = messagechain_builder(imgbase64=imgcontent)
            res = await bot.send(event, msgchain)
            if res == -1:
                await bot.send(event, messagechain_builder(text='截图发送失败'))
        return
