from plugin.preinit.load_application import *
from plugin.preinit.create_bot import *

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
