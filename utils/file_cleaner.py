import os

class filecleaner:

    def __init__(self,foldernames:list):
        self.target = foldernames

    def do_clean(self):
        allfile = []
        for folderpath in self.target:
            allfile.extend(list_allfile(path=folderpath))
        for file in allfile:
            os.remove(file)

def list_allfile(path, all_files=[]):
    if os.path.exists(path):
        files = os.listdir(path)
    else:
        print('this path not exist')
        return
    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            list_allfile(os.path.join(path, file), all_files)
        else:
            all_files.append(os.path.join(path, file))
    return all_files

cleaner = filecleaner(['./images/KissKiss','./images/jupai','./images/MajSoulInfo','./images/PetPet','./images/Remake'])