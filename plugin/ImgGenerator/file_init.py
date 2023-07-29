import os

from utils.cfg_loader import write_file

if not os.path.exists('./images/ImgGenerator'):
    os.mkdir(f'./images/ImgGenerator')
if not os.path.exists(r'./config/ImgGenerator'):
    os.mkdir(r'./config/ImgGenerator')

if not os.path.exists(r'./config/ImgGenerator/config.yml'):
    cfg = {'HoldUpCard': True, 'HoldUp': True, 'Kiss': True, 'Arrest': True, 'SmallLove': True, 'Throw': True,
           'Eat': True, 'BW_img': True, 'Marry': True, 'Screenshot': True, 'CSGOKill': True}
    write_file(content=cfg, path=r'./config/ImgGenerator/config.yml')