from plugin.jupai import *
from plugin.LeisurePlugin import *
from plugin.Petpet import *
from plugin.KissKiss import *
from plugin.MajSoulInfo import *
from plugin.preinit import *
from plugin.Setu import *
from plugin.Remake import *
from plugin.TenHouPlugin import *
from utils import *
from plugin.ImgOperation import *
import os


def create_folders():
    if not os.path.exists("./database"):
        os.mkdir("./database")
    if not os.path.exists("./images"):
        os.mkdir("./images")
    if not os.path.exists("./data"):
        os.mkdir("./data")
    if not os.path.exists("./log"):
        os.mkdir("./log")
    if not os.path.exists('./config'):
        os.mkdir('./config')
