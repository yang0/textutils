import os


def writeConceptFile(filePath, all_concepts):
    cf = open(filePath, 'w')

    for conceptKey in all_concepts:
        concepts = all_concepts[conceptKey]
        if len(concepts) > 1:
            cf.write("\nconcept: ~%s [" % conceptKey)
            for w in concepts:
                cf.write(w + " ")
            cf.write("]")


def writeTable(header, filePath, all_concepts):
    cf = open(filePath, 'w')

    cf.write(header)
    cf.write("Data:\n")

    for conceptKey in all_concepts:
        concepts = all_concepts[conceptKey]
        if len(concepts) > 1:
            for w in concepts:
                cf.write('"%s" "%s"\n' % (w, conceptKey))


class Concepts():
    """
    concept类似同义词的意思
    """

    def __init__(self):
        #词汇到concept的映射
        self.wordDict = {}
        #concept到词汇的映射
        self.conceptDict = {}

        #可编辑的concpet文件单独拿出来，因为要对比更新用
        self.editableFile = ""
        self.editableConceptDict = {}

    #读取目录或者文件
    def read(self, path, isEditable=False):
        assert os.path.exists(path)
        if isEditable:
            self.editableFile = path

        if os.path.isfile(path):
            return self.extractConceptWordsFromFile(path, isEditable=isEditable)

        for file in os.listdir(path):
            if file.endswith(".top"):
                p = os.path.abspath(os.path.join(path, file))
                self.extractConceptWordsFromFile(p)

        return self.conceptDict, self.wordDict

    def saveConcept(self, conceptName, wordsSet, conceptDict):
        if conceptName in self.conceptDict:
            print("重复的concept")
            print(conceptName + "\n")
            print(self.conceptDict[conceptName])
        conceptDict[conceptName] = wordsSet

    def convertSet(self, wordList):
        [w.strip() for w in wordList]
        wordsSet = set(wordList)
        if "" in wordsSet:
            del wordsSet[""]
        return wordsSet

    def extractConceptWordsFromDir(self, path):
        """
        从包含.top文件的目录提取concept
        :param path:
        :return:
        """
        wordsSet = set()
        for file in os.listdir(path):
            if file.endswith(".top"):
                p = os.path.abspath(os.path.join(path, file))
                tset = self.extractWordsFromFile(p)
                wordsSet = wordsSet | tset

        return wordsSet

    def extractConceptWordsFromFile(self, path, isEditable=False):
        """
        从文件中提取concept
        :param path:
        :param isEditable:
        :return:
        """

        with open(path, "r") as f:
            for l in f.readlines():
                l = l.strip()
                if l.startswith("concept:"):
                    s = l[l.find("[") + 1:l.find("]")]
                    wordList = s.split()
                    wordsSet = self.convertSet(wordList)

                    conceptName = l[l.find("~")+1 : l.find("[")].strip()

                    self.saveConcept(conceptName, wordsSet, self.conceptDict)
                    if isEditable:
                        self.saveConcept(conceptName, wordsSet, self.editableConceptDict)

                    for w in wordsSet:
                        if w not in self.wordDict:
                            self.wordDict[w] = set()
                        self.wordDict[w].add(conceptName)

        return self.conceptDict, self.wordDict


    def getConceptNames(self, word):
        return self.wordDict[word]

    def getWord(self, conceptName):
        return self.conceptDict[conceptName]

    def haveWord(self, word):
        return word in self.wordDict

    def haveConcept(self, conceptName):
        return conceptName in self.conceptDict

    def getConceptString(self, conceptName):
        """
        获取concept
        :param conceptName:
        :return:以字符串形式返回concept
        """
        if not self.haveConcept(conceptName):
            return ""
        return conceptName + ":" + " ".join(list(self.getWord(conceptName)))

    def search(self, w):
        """
        搜索关键词是否存在于concept（名称or集合）中
        :param w: 关键词
        :return: 以字符串形式返回结果，concept之间用;隔开
        """
        str = ""
        if self.haveWord(w):
            for conceptName in self.getConceptNames(w):
                str += self.getConceptString(conceptName) + " ; \n"
        elif self.haveConcept(w):
            str = self.getConceptString(w)

        return str




    def updateConceptDict(self, conceptName, wordsSet, conceptDict):
        if conceptName in conceptDict:
            oldSet = conceptDict[conceptName]
            newSet = oldSet | wordsSet
            conceptDict[conceptName] = newSet
        else:
            conceptDict[conceptName] = wordsSet


    def save(self, conceptList):
        """
        保存新的或者要修改的concept
        :param conceptList:
        :return:
        """
        needUpdateConceptFile = False
        for c in conceptList:
            if len(c.strip()) < 5:
                continue
            conceptName = c[:c.find(":")].strip()
            words = c[c.find(":")+1 :].strip().split()
            wordsSet = self.convertSet(words)

            print(conceptName + ": ")
            print(wordsSet)

            #更新concept内存
            self.updateConceptDict(conceptName, wordsSet, self.conceptDict)
            self.updateConceptDict(conceptName, wordsSet, self.editableConceptDict)
            if conceptName in self.editableConceptDict:
                needUpdateConceptFile = True

            # 更新word内存
            for w in wordsSet:
                if w in self.wordDict:
                    self.wordDict[w].add(conceptName)
                else:
                    vSet = set()
                    vSet.add(conceptName)
                    self.wordDict[w] = vSet

        #更新文件
        if needUpdateConceptFile:
            writeConceptFile(self.editableFile, self.editableConceptDict)

    def replaceConcpet(self, word):
        """
        如果词汇包含在某个concept中，那么将改词转化成concpet.
        :param word:
        :return:
        """
        conceptName = word
        getOne = lambda x: next(iter(x))
        if word in self.wordDict:
            conceptName = "~"+getOne(self.wordDict[word])
            print(conceptName)
            if conceptName == "~药物":
                conceptName = word

        return conceptName


    def filter(self, wordList):
        """
        替换包含concepts的词，并且返回用到的所有concept
        :param wordList:
        :return:
        """
        resultList =  [self.replaceConcpet(w) for w in wordList]

        conceptsUsed = {}
        for w in resultList:
            if w[0] == "~":
                conceptName = w[1:]
                conceptsUsed[conceptName] = self.conceptDict[conceptName]

        return resultList, conceptsUsed


