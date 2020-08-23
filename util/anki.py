# 对从每日英语听力拷贝出来的文本进行排序，便于导入anki
import os
import re


def sortText(file_path):
    enlist = []
    cnlist = []
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    with open(file_path, "r") as f:
        for line in f.readlines():
            if line.isspace():
                continue
            line = line.strip()
            is_en = not zhPattern.search(line)

            # print(f'{line}；纯英文：{is_en}; 空格{is_space}')
            if not is_en:
                cnlist.append(line)
            else:
                enlist.append(line)
    return enlist, cnlist

            
def makeSentences(srcDir, targetFile):
    os.chdir(srcDir)
    files = os.listdir(srcDir)
    with open(targetFile,"w") as output:
        for file in files:
            en, cn = sortText(file)
            output.writelines(["<br>".join(cn), "|", "<br>".join(en), "\n"])
        

def makeOneSentence(srcDir, targetFile):
    os.chdir(srcDir)
    files = os.listdir(srcDir)
    with open(targetFile,"w") as output:
        for file in files:
            
            en, cn = sortText(file)
            if len(cn) != len(en):
                print(f'{file},cn: {len(cn)}, en:{len(en)}')
                print("不相符")
                continue
            lines = []
            for inx in range(0, len(en)):
                s = en[inx] + "|" + cn[inx] + "\n"
                lines.append(s)
            output.writelines(lines)



def makeFiles(srcDir):
    for i in range(1,381):
        s = "%03d" % i
        file = open(f'{srcDir}/{s}.txt','w')
        file.close()

# 批量创建文件
# makeFiles("/e/anki/family")

# 转文本
makeOneSentence("/e/anki/family","/e/anki/family.txt")




