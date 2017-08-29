
import linecache, os


from itertools import (takewhile,repeat)


#计算文件的总行数
def rawbigcount(filename):
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum( buf.count(b'\n') for buf in bufgen if buf )


class LineReader():
    """
    支持双向逐行读取一个文件
    """

    def __init__(self, fileName, currentLine=1):
        assert os.path.exists(fileName)
        self.fileName = fileName
        self.currentLine = currentLine
        self.linesCount = rawbigcount(fileName)

    def clearCache(self):
        linecache.clearcache()

    def hasNext(self):
        if self.currentLine >= self.linesCount:
            return False
        return True

    def load(self, currentLine=1):
        self.currentLine = currentLine
        return self.reload()

    def reload(self):
        if self.currentLine > 0:
            return linecache.getline(self.fileName, self.currentLine)

    def next(self, num=1):
        if self.currentLine + num > self.linesCount:
            return

        if num == -1:
            self.currentLine = self.linesCount
        else:
            self.currentLine += num
        s = linecache.getline(self.fileName, self.currentLine)
        return s



    def hasPrev(self):
        if self.currentLine <= 1:
            return False
        return True


    def prev(self, num):
        if self.currentLine - num < 1:
            return

        if num == -1:
            self.currentLine = 1
        else:
            self.currentLine -= num
        s = linecache.getline(self.fileName, self.currentLine)
        return s
