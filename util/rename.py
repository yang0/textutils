import os
import re

srcDir = input("请输入目录名称:")
targetName = input("请输入文件名:")

os.chdir(srcDir)
files = os.listdir(srcDir)
pattern="Track (\d*.mp3)"
for file in files:
    s = re.findall(pattern, file)
    os.rename(file, targetName + s[0])

print(os.listdir(srcDir))