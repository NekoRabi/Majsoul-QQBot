import os

# files = os.listdir("")

i = 0
for parent, dirnames, filenames in os.walk("."):
    for filename in filenames:
        # print("parent is: " + parent)
        # print("filename is: " + filename)
        print(os.path.join(parent, filename))  # 输出rootdir路径下所有文件（包含子文件）信息
        newName = f'cheshire{i}.{filename.split(".")[1]}'
        os.rename(os.path.join(parent, filename), os.path.join(parent, newName))
        i = i + 1
