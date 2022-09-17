"""
:Author:  NekoRabi
:Create:  2022/9/18 3:25
:Update: /
:Describe: 垃圾自动清理
:Version: 0.0.1
"""
import os

__all__ = ['cleaner', 'FileCleaner']


class FileCleaner:

    def __init__(self, foldernames: list):
        self.target = foldernames
        self.do_clean()

    def do_clean(self):
        _allfile = []
        print("开始清理文件")
        for folderpath in self.target:
            if os.path.exists(folderpath):
                _allfile.extend(list_allfile(path=folderpath))
        try:
            print(f'发现 {len(_allfile)} 个文件')
            for file in _allfile:
                os.remove(file)
            print("清理完成")
        except FileNotFoundError as e:
            print(f"清理失败\t{e}")


def list_allfile(path, all_files=None):
    if all_files is None:
        all_files = []
    if os.path.exists(path):
        files = os.listdir(path)
    else:
        # print('文件不存在')
        return all_files
    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            list_allfile(os.path.join(path, file), all_files)
        else:
            all_files.append(os.path.join(path, file).replace("\\\\", "/"))
    return all_files


# TODO 垃圾清理的路径自定义,而不是通过代码写死

cleaner = FileCleaner(
    ['./images/KissKiss', './images/jupai', './images/MajSoulInfo', './images/PetPet', './images/Remake',
     './images/ImgOperation', './images/daibu'])
