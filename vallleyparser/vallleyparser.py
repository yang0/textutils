
import PyQt5.QtCore as core
from PyQt5.Qt import *
from PyQt5.QtWidgets import QMainWindow
from vallleyparser import valleyutil
# pyrcc5  -o valleyutil.py ./valleyutil.qrc

import inspect, os
from util.linereader import LineReader
from util.jiebautil import DictWords, cutWords
from PyQt5.Qt import QObject
import json
from util.conceptutil import Concepts

from util import configutil, jsonutil

def currentDir():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def absPath(relativePath):
    return os.path.join(currentDir(), relativePath)


class ValleyDict(QObject):

    dictSaved = core.pyqtSignal()
    garbageRemoved = core.pyqtSignal()

    def __init__(self):
        super(QObject, self).__init__()
        self.dictWords = DictWords()

    def convertSet(self, str):
        """
        把字符串转换成set
        :param str:
        :return:
        """
        if str.strip() == "":
            return set()
        words = str.strip().split()
        words = [w.strip() for w in words]
        wordsSet = set(words)
        if "" in wordsSet:
            del wordsSet[""]

        return wordsSet


    @core.pyqtSlot(str)
    def save(self, str):
        """
        将分词保存起来
        :param str: 以空格区分的分词字符串
        :return: 最后不返回结果，只发出signal
        """

        wordsSet = self.convertSet(str)

        if len(wordsSet) > 0:
            self.dictWords.append(wordsSet)

        self.dictSaved.emit()

    @core.pyqtSlot(str)
    def stop(self, str):
        """
        保存停用词
        :param str: 以空格区分的分词字符串
        :return:
        """
        wordsSet = self.convertSet(str)
        self.dictWords.stop(wordsSet)

        self.dictSaved.emit()

    @core.pyqtSlot(str)
    def saveGarbageWords(self, str):
        """
        保存垃圾词汇，删除垃圾记录，然后重新加载
        :param str: 以空格区分的分词字符串
        :return:
        """
        wordsSet = self.convertSet(str)
        garbageUtil = jsonutil.GarbageUtil()
        garbageUtil.saveGarbageWords(wordsSet)
        garbageUtil.removeGarbageRecord()

        self.garbageRemoved.emit()


    def filter(self, sentence):
        return self.dictWords.extractTags(sentence)





class ValleyConcepts(QObject):

    conceptsSaved = core.pyqtSignal()
    conceptSearched = core.pyqtSignal(str)

    def __init__(self):
        super(QObject, self).__init__()

        self.concepts = Concepts()
        self.loadConcepts()


    def loadConcepts(self):
        conceptFiles = configutil.config["concepts"]["readable_concepts"].split()
        for c in conceptFiles:
            self.concepts.read(c)
        editableConcept = configutil.config["concepts"]["eidtable_concept"]
        self.concepts.read(editableConcept, isEditable=True)

    @core.pyqtSlot(str)
    def save(self, str):
        self.concepts.save(str.split("\n"))
        self.conceptsSaved.emit()

    @core.pyqtSlot(str)
    def search(self, w):
        """
        搜索concept
        :param w:
        :return:
        """
        result = self.concepts.search(w)
        self.conceptSearched.emit(result)

    def filter(self, wordsList):
        reservedWords, conceptsUsed = self.concepts.filter(wordsList)
        s = ""
        ignoreConceptNames = configutil.config["concepts"]["eidtable_concept"].split()
        for conceptName in conceptsUsed:
            if conceptName in ignoreConceptNames:
                continue
            concepts = list(conceptsUsed[conceptName])
            s += conceptName + " : " + " ".join(concepts) + "\n"

        return reservedWords, s




class Valleys(QObject):
    valleyRecieved = core.pyqtSignal(str, str, str, str, int)
    readPointFile = "readpoint.txt"
    jsonFile = configutil.config["json"]["path"]
    questionField = configutil.config["json"]["question_field"]
    answerField = configutil.config["json"]["answer_field"]

    def __init__(self, concepts, valleyDict):
        super(QObject, self).__init__()
        self.lineReader = LineReader(self.jsonFile)
        self.restoreRunPoint()
        self.concepts = concepts
        self.valleyDict = valleyDict

    def saveRunPoint(self):
        with open(absPath(self.readPointFile), "w") as f:
            f.write(str(self.lineReader.currentLine))

    def restoreRunPoint(self):
        if not os.path.exists(absPath(self.readPointFile)):
            self.lineReader.currentLine = 1
            return
        with open(absPath(self.readPointFile), "r") as f:
            l = f.read().strip()
            self.lineReader.currentLine = int(l)



    def getValley(self, str):
        print(str)
        data = json.loads(str)

        answerKeys = self.answerField.split(".")
        question = jsonutil.recursive_get(data, self.questionField)
        answer = jsonutil.recursive_get(data, self.answerField)

        cutStr = cutWords(question)

        reservedWords = self.valleyDict.extractTags(question)
        reservedWords, conceptsUsedStr = self.concepts.extractTags(reservedWords)

        self.valleyRecieved.emit(question+answer, cutStr, " ".join(reservedWords), conceptsUsedStr, self.lineReader.currentLine)

        self.saveRunPoint()


    @core.pyqtSlot(int)
    def next(self, num):
        if not self.lineReader.hasNext():
            return "", ""
        self.getValley(self.lineReader.next(num))

    @core.pyqtSlot(int)
    def prev(self, num):
        if not self.lineReader.hasPrev():
            return "", ""
        self.getValley(self.lineReader.prev(num))


    @core.pyqtSlot()
    def reload(self):
        self.getValley(self.lineReader.reload())

    @core.pyqtSlot()
    def loadFirstRecord(self):
        """
        垃圾信息删除后，重新定位到第一条记录
        :return:
        """
        self.lineReader = LineReader(self.jsonFile)
        self.lineReader.currentLine = 1
        self.lineReader.clearCache()
        self.getValley(self.lineReader.reload())







class ValleyParserWindow(QMainWindow):

    def __init__(self, parent=None):
        super(ValleyParserWindow,self).__init__()

        self.concepts = ValleyConcepts()
        self.valleyDict = ValleyDict()
        self.valleys = Valleys(self.concepts, self.valleyDict)
        self.concepts.conceptsSaved.connect(self.valleys.reload)
        self.valleyDict.dictSaved.connect(self.valleys.reload)
        self.valleyDict.garbageRemoved.connect(self.valleys.loadFirstRecord)


        self.wv = QWebEngineView()
        self.setCentralWidget(self.wv)


        with open(absPath("./index.html")) as f:
            self.wv.setHtml(f.read())

        channel = QWebChannel(self.wv.page())
        channel.registerObject('valleys', self.valleys)
        channel.registerObject('concepts', self.concepts)
        channel.registerObject('valleyDict', self.valleyDict)
        self.wv.page().setWebChannel(channel)
        self.wv.show()

    @core.pyqtSlot()
    def doIt(self):
        print('running a long process...')
        print('of course it should be on a thread...')
        print('and the signal should be emmited from there...')
        self.proccessFinished.emit()

def runApp():
    app = QApplication([])
    mw = ValleyParserWindow()
    mw.show()
    app.exec_()

if __name__ == '__main__':
    runApp()