import base64
from io import BytesIO

from PIL import Image as IMG


def mergeimgs(urls: list) -> IMG:
    imgback = IMG.new("RGB", (1020, 420), (255, 255, 255))
    for i in range(10):
        img = IMG.open(f'./plugin/MajSoulInfo/{urls[i]}').convert("RGBA")
        img = img.resize((180, 180), IMG.ANTIALIAS)
        r, g, b, a = img.split()
        posx = 20 + (i % 5) * 200
        posy = 20 + (i // 5) * 200
        imgback.paste(img, (posx, posy, posx + img.size[0], posy + img.size[1]), mask=a)
    # imgback.save(fp=f"./images/MajSoulInfo/{senderid}.png")
    img = img_to_base64(imgback)
    return img

def img_to_base64(PILimg: IMG = None):
    """
    图片转换为base64的格式

    Args:
        PILimg: PIL的图片

    Returns:base64的图片

    """
    img_bytes = BytesIO()

    PILimg.save(img_bytes, format='PNG')
    b_content = img_bytes.getvalue()
    imgcontent = base64.b64encode(b_content)
    return imgcontent