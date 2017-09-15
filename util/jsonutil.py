import os, json
import codecs
from util import jiebautil, configutil
from util.linereader import LineReader
import jieba.analyse as jiebays
from functools import reduce
import shutil

def getJsonInDir(dir):
    """
    读取目录下的所有json文件，一般来自爬虫抓取的资料。一个文件保存一个json格式
    :param dir:
    :return: 返回字典类型
    """
    fileIgnored = 0
    for jsonFile in os.listdir(dir):

        with codecs.open(dir + "/" + jsonFile, "r", encoding='utf-8', errors='ignore') as f:
            try:
                j = json.load(f)
            except:
                fileIgnored += 1
                continue

            yield j




def iterJsonLine(jsonFile):
    """
    返回json对象，一行一个
    :param jsonFile:
    :return:
    """
    lineReader = LineReader(jsonFile)
    while lineReader.hasNext():
        line = lineReader.next()
        j = json.loads(line)

        yield j


def iterJsonValue(jsonFie, fieldNames):
    """
    从单独的json文件中加载文本
    :param fieldNameDict:
    :return: 返回 dictionary
    """
    result = {}
    for j in iterJsonLine(jsonFie):
        for k in fieldNames:
            result[k] = recursive_get(j, k)
        yield result


def iterJsonString(jsonFie, fieldNames):
    """
    从单独的json文件中加载文本，将值合并成一个字符串返回
    :param fieldNameDict:
    :return:
    """
    for r in iterJsonValue(jsonFie, fieldNames):
        s = " ".join(r.values())
        yield s


def iterCutField(jsonFile, fieldNames):
    """
    从单独的json文件中加载文本，把所有字段连接起来，然后分词
    :param jsonFile:
    :param fieldNames:
    :return:
    """

    for j in iterJsonValue(jsonFile, fieldNames):
        yield jiebautil.cutWords(" ".join(j.values()))


def iterCutFieldList(jsonFile, fieldNames):
    """
    返回list形式的数据
    :param jsonFile:
    :param fieldNames:
    :return:
    """
    for s in iterCutField(jsonFile, fieldNames):
        yield s.split()


def iterTopKeyWords(jsonFile, fieldNames, topK=5):
    """
    返回topK个关键词
    :param jsonFile:
    :param fieldNames:
    :param topK:
    :return:
    """
    for j in iterJsonValue(jsonFile, fieldNames):
        yield jiebays.extract_tags(" ".join(j.values()), topK=topK)


def getKeywords(jsonFile, fieldNames, topK=10):
    """
    取值范围为所有文本，统计出topK个关键词
    :param jsonFile:
    :param fieldNames:
    :param topK:
    :return:
    """
    s = ""
    # for j in iterJsonValue(jsonFile, fieldNames):
    #     s += " ".join(j.values())

    for j in iterTopKeyWords(jsonFile, fieldNames, topK):
        s += " ".join(j)

    return jiebays.extract_tags(s, topK=topK)


def saveCutFile(jsonFile, fieldNames):
    """
    将json文件中的字段分词后保存到一个文本文件中，便于word2vec使用
    :param jsonFile:
    :param fieldNames:
    :return:
    """

    cutFile = configutil.config["json"]["cut_file"]
    print("开始写入文件：%s" % cutFile)
    with open(cutFile, "w") as f:
        for s in iterCutField(jsonFile, fieldNames):
            f.write(s+"\n")
    print("保存文件完毕：%s" % cutFile)


def recursive_get(d, keyStr):
    """
    处理json 多级嵌套的情况。比如关键词在result.title这个字段
    :param d:
    :param keys:
    :return:
    """
    keys  = keyStr.split(".")
    result = reduce(lambda c, k: c.get(k, {}), keys, d)
    if type(result) == dict:
        result = ""
    else:
        result = result.strip().replace(' ', '')

    return result


class GarbageUtil():



    def __init__(self):
        self.garbageDict = configutil.config["other"]["garbage_words"]
        self.jsonFile = configutil.config["json"]["path"]
        self.questionField = configutil.config["json"]["question_field"]
        self.answerField = configutil.config["json"]["answer_field"]
        self.garbageSet = ()



    def saveGarbageWords(self, vSet):
        """
        保存垃圾词汇，只要出现垃圾词汇的问答一律删除
        :param words:
        :return:
        """
        self.loadGarbageWords()
        with open(self.garbageDict, "a") as f:
            for w in vSet:
                if not w in self.garbageSet:
                    self.garbageSet.add(w)
                    f.write("\n" + w)

        dictWords = jiebautil.DictWords()
        dictWords.append(self.garbageSet)

    def loadGarbageWords(self):
        if not os.path.exists(self.garbageDict):
            return
        with open(self.garbageDict, "r") as f:
            l = f.readlines()
            l = [w.strip() for w in l if w.strip() != ""]
            self.garbageSet = set(l)

        print(self.garbageSet)


    def removeGarbageRecord(self):
        """
        从json文件中删除垃圾记录
        :return:
        """
        tmp_file = self.jsonFile+".tmp"
        bak_file = self.jsonFile+".bak"
        self.loadGarbageWords()

        tf = open(tmp_file, "w")
        result = {}
        for j in iterJsonLine(self.jsonFile):
            question = recursive_get(j, self.questionField)
            answer = recursive_get(j, self.answerField)
            s = question + " " + answer
            garbageFound = False
            for w in jiebautil.cutWords(s).split():
                if w.strip() in self.garbageSet:
                    garbageFound = True
                    print(question)
                    continue

            if not garbageFound:
                s = json.dumps(j)
                tf.write(s + "\n")

        shutil.move(self.jsonFile, bak_file)
        shutil.move(tmp_file, self.jsonFile)





