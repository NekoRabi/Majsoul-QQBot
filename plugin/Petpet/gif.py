from PIL import Image as IMG
from PIL import ImageOps
from moviepy.editor import ImageSequenceClip
import numpy
import aiohttp
from io import BytesIO
import os

# 插件信息
__name__ = "PetPet"
__description__ = "生成摸头gif"
__usage__ = "在群内发送 摸@目标 即可"


async def petpet_generator(qqnumber: int):
    if not os.path.exists("./images/PetPet"):
        os.mkdir("./images/PetPet")
    if not os.path.exists("./images/PetPet/temp"):
        os.mkdir("./images/PetPet/temp")
    await petpet(member_id=qqnumber)
    return


frame_spec = [
    (27, 31, 86, 90),
    (22, 36, 91, 90),
    (18, 41, 95, 90),
    (22, 41, 91, 91),
    (27, 28, 86, 91)
]

squish_factor = [
    (0, 0, 0, 0),
    (-7, 22, 8, 0),
    (-8, 30, 9, 6),
    (-3, 21, 5, 9),
    (0, 0, 0, 0)
]

squish_translation_factor = [0, 20, 34, 21, 0]

frames = tuple([f'./plugin/Petpet/PetPetFrames/frame{i}.png' for i in range(5)])


async def save_gif(gif_frames, dest, fps=10):
    """生成 gif
    将输入的帧数据合并成视频并输出为 gif
    参数
    gif_frames: list<numpy.ndarray>
    为每一帧的数据
    dest: str
    为输出路径
    fps: int, float
    为输出 gif 每秒显示的帧数
    返回
    None
    但是会输出一个符合参数的 gif
    """
    # clip = ImageSequenceClip(gif_frames, fps=fps)
    # clip.write_gif(dest, program='ffmpeg', logger=None, logger=None)  # 使用 imageio
    # clip.close()
    with ImageSequenceClip(gif_frames, fps=fps) as clip:
        clip.write_gif(dest, program='ffmpeg', logger=None)


# 生成函数（非数学意味）
async def make_frame(avatar, i, squish=0, flip=False):
    """生成帧
    将输入的头像转变为参数指定的帧，以供 make_gif() 处理
    参数
    avatar: PIL.Image.Image
    为头像
    i: int
    为指定帧数
    squish: float
    为一个 [0, 1] 之间的数，为挤压量
    flip: bool
    为是否横向反转头像
    返回
    numpy.ndarray
    为处理完的帧的数据
    """
    # 读入位置
    spec = list(frame_spec[i])
    # 将位置添加偏移量
    for j, s in enumerate(spec):
        spec[j] = int(s + squish_factor[i][j] * squish)
    # 读取手
    hand = IMG.open(frames[i])
    # 反转
    if flip:
        avatar = ImageOps.mirror(avatar)
    # 将头像放缩成所需大小
    avatar = avatar.resize((int((spec[2] - spec[0]) * 1.2), int((spec[3] - spec[1]) * 1.2)), IMG.ANTIALIAS)
    # 并贴到空图像上
    gif_frame = IMG.new('RGB', (112, 112), (255, 255, 255))
    gif_frame.paste(avatar, (spec[0], spec[1]))
    # 将手覆盖（包括偏移量）
    gif_frame.paste(hand, (0, int(squish * squish_translation_factor[i])), hand)
    # 返回
    return numpy.array(gif_frame)


async def petpet(member_id, flip=False, squish=0, fps=15) -> None:
    """生成PetPet
    将输入的头像生成为所需的 PetPet 并输出
    参数
    path: str
    为头像路径
    flip: bool
    为是否横向反转头像
    squish: float
    为一个 [0, 1] 之间的数，为挤压量
    fps: int
    为输出 gif 每秒显示的帧数
    返回
    bool
    但是会输出一个符合参数的 gif
    """

    if not os.path.exists("./images/PetPet/temp"):
        os.mkdir("./images/PetPet/temp")
    if os.path.exists(f'./images/PetPet/temp/tempPetPet-{member_id}.gif'):
        os.remove(f'./images/PetPet/temp/tempPetPet-{member_id}.gif')
    url = f'http://q1.qlogo.cn/g?b=qq&nk={str(member_id)}&s=640'
    gif_frames = []
    # 打开头像
    # avatar = Image.open(path)
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()

    avatar = IMG.open(BytesIO(img_content)).convert("RGBA")

    size = avatar.size
    # 因为是要圆形，所以需要正方形的图片
    r2 = min(size[0], size[1])
    ima = avatar
    if size[0] != size[1]:
        ima = avatar.resize((r2, r2), IMG.ANTIALIAS)
    # 最后生成圆的半径
    r3 = r2 // 2
    imb = IMG.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 1))
    pima = ima.load()  # 像素的访问对象
    pimb = imb.load()
    r = float(r2 / 2)  # 圆心横坐标

    for i in range(2 * r3):
        for j in range(2 * r3):
            lx = abs(i - r)  # 到圆心距离的横坐标
            ly = abs(j - r)  # 到圆心距离的纵坐标
            l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径
            if l < r3:
                pimb[i - (r - r3), j - (r - r3)] = pima[i, j]
    # 生成每一帧
    for i in range(5):
        gif_frames.append(await make_frame(imb, i, squish=squish, flip=flip))
    # 输出
    await save_gif(gif_frames, f'./images/PetPet/temp/tempPetPet-{member_id}.gif', fps=fps)
