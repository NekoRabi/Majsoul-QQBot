import os

if not os.path.exists("./database"):
    os.mkdir("./database")
if not os.path.exists("./images"):
    os.mkdir("./images")
if not os.path.exists("./data"):
    os.mkdir("./data")
if not os.path.exists(r'./data/fonts'):
    os.mkdir(r'./data/fonts')
if not os.path.exists("./log"):
    os.mkdir("./log")
if not os.path.exists('./config'):
    os.mkdir('./config')
