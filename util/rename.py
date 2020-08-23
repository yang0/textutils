import os
import re
import eyed3

# 本例用的python3.7


def renameLevel2Files(srcDir):
    book_dirs = os.listdir(srcDir)
    # pattern="(\d*) 曲目 \d*.mp3"
    for book_dir in book_dirs:
        os.chdir(srcDir)
        abspath = os.path.abspath(book_dir)
        os.chdir(abspath)
        files = os.listdir(abspath)
        book_name = book_dir[2:]
        for file in files:
            print(file)
            s = re.findall(pattern, file)
            targetFile = book_name + s[0] + ".mp3"
            os.rename(file, targetFile)
            audiofile = eyed3.load(targetFile)
            audiofile.tag.title = book_name + s[0]
            audiofile.tag.save()


def rename2(srcDir: str):
    files = os.listdir(srcDir)
    for file in files:
        if file[:4] == 'razh':
            continue
        print(file)
        targetFile = f'razh_{file}'
        print(targetFile[:-4])
        os.rename(file, targetFile)
        audiofile = eyed3.load(targetFile)
        audiofile.tag.title = targetFile[:-4]
        audiofile.tag.save()


def rename(srcDir: str):
    files = os.listdir(srcDir)
    for file in files:
        print(file)
        targetFile = f'Pinocchio_{file[:2]}'
        print(targetFile[:-4])
        os.rename(file, targetFile)
        audiofile = eyed3.load(targetFile)
        audiofile.tag.title = targetFile[:-4]
        audiofile.tag.save()

# srcDir = input("请输入目录名称:")
# srcDir = "/e/temp/razh/"
# targetName = input("请输入文件名:")
srcDir = "/e/temp/Pinocchio/"
os.chdir(srcDir)

rename(srcDir)




# print(os.listdir(srcDir))