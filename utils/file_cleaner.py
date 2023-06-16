"""
:Author:  NekoRabi
:Create:  2022/9/18 3:25
:Update: /
:Describe: 垃圾自动清理
:Version: 0.0.1
"""
import os

__all__ = ['cleaner', 'FileCleaner']

from utils.cfg_loader import read_file


class FileCleaner:

    def __init__(self, foldernames: list):
        self.target_folders = foldernames
        self.do_clean()
        print(f'需要清理垃圾的文件路径为{self.target_folders}')

    def do_clean(self):
        if len(self.target_folders) == 0:
            return
        _allfile = []
        print("开始清理文件")
        for folderpath in self.target_folders:
            if os.path.exists(folderpath):
                _allfile.extend(list_allfile(path=folderpath))
        try:
            print(f'发现 {len(_allfile)} 个文件')
            for file in _allfile:
                os.remove(file)
            print("清理完成")
        except FileNotFoundError as e:
            print(f"清理失败\t{e}")

    def addtarget(self, folder_path: str or list):
        if type(folder_path) is list:
            for path in folder_path:
                try:
                    self.target_folders.append(f'{path}')
                except Exception as _e:
                    print(_e)
        elif type(folder_path) is str:
            self.target_folders.append(folder_path)
        else:
            raise TypeError('垃圾文件夹路径类型无效,仅接受str和list')


def list_allfile(path, all_files=None):
    if all_files is None:
        all_files = []
    if os.path.exists(path):
        files = os.listdir(path)
    else:
        # print('路径不存在')
        return all_files
    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            list_allfile(os.path.join(path, file), all_files)
        else:
            all_files.append(os.path.join(path, file).replace("\\\\", "/"))
    return all_files


# _folders = read_file(r'./config/config.yml').get('trash_folders', [])
_folders = read_file(r'./config/config.yml').get('trash_folders', [])

cleaner = FileCleaner(_folders)
