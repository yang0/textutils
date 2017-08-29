#读取和写入分词字典

import os, collections

import jieba
import sys
from util import configutil
import jieba.analyse as jiebays

STOP_WORDS = configutil.config["jieba"]["stop_dict"]
USER_DICT = configutil.config["jieba"]["user_dict"]


DICT_LIST = [USER_DICT]

stopwordset = set()
DICT_LOADED = False

def loadDict():
    global  DICT_LOADED
    if not DICT_LOADED:
        loadStopWords()
        loadUserDicts()
    DICT_LOADED = True


def loadUserDicts():
    for dict in DICT_LIST:
        jieba.load_userdict(dict)

def loadUserDict():
    jieba.load_userdict(USER_DICT)

#定义停词
def loadStopWords():
    global stopwordset
    with open(STOP_WORDS, 'r', encoding='utf-8') as sw:
        stopwordset = sw.readlines()
        stopwordset = [x.strip() for x in stopwordset]

def cutWords(s, cutAll=False):
    loadDict()
    words = jieba.cut(s, cut_all=cutAll)
    words = [w for w in words if w not in stopwordset]
    return ' '.join(words)


#将多组会话分词
def cutConversations(conversations):
    loadDict()
    newConversations = []
    for conversation in conversations:
        #print(conversation[1])
        newConversation = [cutWords(conversation[0]).strip(), "\n", cutWords(conversation[1]).strip(), "\n", "E", "\n"]
        if newConversation[0] != "" and newConversation[2] != "":
            newConversations += newConversation

    return newConversations


class DictWords(set):
    """
    用来操作用户字典和停用词字典的类
    """
    def __init__(self):
        super(set, self).__init__()
        loadDict()
        self.loadWords()

    def loadWords(self):
        for dict in DICT_LIST:
            with open(dict, "r") as f:
                for w in f:
                    self.add(w.strip())
        print("字典长度 %i" % len(self))

    def append(self, value):
        vSet = set()

        if isinstance(value, str):
            if value in self:
                return
            else:
                vSet.add(value)
                self.add(value)


        if isinstance(value, collections.Iterable):
            for w in value:
                if not isinstance(w, str) or w in self:
                    continue
                vSet.add(w)
                self.add(w)
            if len(vSet) == 0:
                return
        else:
            return

        self.appendFile(vSet, USER_DICT)
        loadUserDict()

    def stop(self, wordSet):
        """
        保存停用词
        :param wordSet:
        :return:
        """
        global stopwordset

        vSet=set()
        for w in wordSet:
            if w in stopwordset:
                continue
            vSet.add(w)

        if len(vSet) == 0:
            return

        stopwordset = stopwordset | wordSet
        self.appendFile(vSet, STOP_WORDS)


    def appendFile(self, vSet, file):
        with open(file, "a") as f:
            for w in vSet:
                f.write("\n"+w)

    #将不在字典里的词汇过滤掉
    def filter(self, wordList):
        return [w for w in wordList if w in self]


    def extractTags(self, sentence):
        """
        使用jieba默认的tfidf算法，取得句子中topN的关键词
        :param sentence:
        :return:
        """
        topK = configutil.config.getint("json","keywords_num")
        return jiebays.extract_tags(sentence, topK=topK)


