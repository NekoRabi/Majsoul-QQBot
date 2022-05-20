from plugin.LeisurePlugin.leisure import *
from plugin.LeisurePlugin.tarot import TarotCards,TarotCard
import os

if not os.path.exists("./database/LeisurePlugin"):
    os.mkdir("./database/LeisurePlugin")

if not os.path.exists("./images/tarot"):
    os.mkdir("./images/tarot")
