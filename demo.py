

from util import jsonutil, tfidfutil, jiebautil, configutil
from util.mongoutil import MongoUtil
import classify
import jieba.analyse as jiebays
from skutil.findK import findk
from skutil import kmeans
from util.linereader import LineReader
import json

JSON_FILE = configutil.config["json"]["path"]
QUESTION_FIELD = configutil.config["json"]["question_field"]
ANSWER_FIELD = configutil.config["json"]["answer_field"]





def insertMongo(dbName, collectionName):
    """
    录入mongodb，录入的格式只适用于chatscript
    :return:
    """
    mongoutil = MongoUtil(dbName, collectionName)

    for result in jsonutil.IterJsonFile(JSON_FILE, {QUESTION_FIELD, ANSWER_FIELD}):
        if result['answer'].strip() != "":
            mongoutil.insert(result['title'], result['answer'])


def getTfIdf():
    classify.getTfIdf()


def getTopKeyWordsByJieba(topK=5):
    """
    直接使用jieba提供的函数，取得topN关键词
    :param topK:
    :return:
    """
    for tags in jsonutil.iterTopKeyWords(JSON_FILE, {QUESTION_FIELD}, topK=topK):
        print(tags)


def getTopKeyWords(topK=5):
    """
    通过自建idf来获取topN关键词, 感觉效果还没有直接用jieba的好
    :param topK:
    :return:
    """

    iterableString = jsonutil.iterCutField(JSON_FILE, {QUESTION_FIELD, ANSWER_FIELD})
    idfLoader = tfidfutil.IDFLoader()
    idfLoader.makeIdfFile(iterableString)
    tfidf = tfidfutil.TFIDF(idfLoader)

    for j in jsonutil.iterJsonValue(JSON_FILE, {'title'}):
        s = " ".join(j.values())
        print(s)

        tags = tfidf.extract_keywords(s, topK)
        print(tags)

        tag2 = jiebays.extract_tags(s, topK=topK, withWeight=True)
        print(tag2)


def cutWords(sentence):
    print(jiebautil.cutWords(sentence))


def findK(topK=10, keywordsNum=10):
    """
     对多个文本寻找合适的分类数量，也就是K值
    :param topK:
    :param keywordsNum:
    :return:
    """
    iterString = jsonutil.iterJsonString(JSON_FILE, {QUESTION_FIELD, ANSWER_FIELD})
    findk(iterString, topK, keywordsNum)



def classify(clusterNum):
    """
    对文本分类
    :return:
    """
    iterString = jsonutil.iterJsonString(JSON_FILE, {QUESTION_FIELD, ANSWER_FIELD})
    result = kmeans.classify(iterString, clusterNum)

    lineReader = LineReader(JSON_FILE)
    for indexList in result:
        print("=============================================")
        for index in indexList:
            #行号需要加1
            l = lineReader.load(index+1)
            j = json.loads(l)
            print(jsonutil.recursive_get(j, QUESTION_FIELD))




def search(words):
    """
    搜索包含关键词的文本
    :param words:
    :return:
    """
    results = jsonutil.iterJsonValue(JSON_FILE, [QUESTION_FIELD, ANSWER_FIELD])
    for result in results:
        s = " ".join(result.values())
        strList = jiebautil.cutWords(s).split()
        if all(w in strList for w in words):
            for k in result:
                print("".join(result[k].split()))
            print("\n")

def saveCutFile():
    """
    将json文件中的字段分词后保存到一个文本文件中，便于word2vec使用
    :return:
    """
    jsonutil.saveCutFile(JSON_FILE, [QUESTION_FIELD, ANSWER_FIELD])


def getKeywords(topN):
    print(jsonutil.getKeywords(JSON_FILE, {QUESTION_FIELD, ANSWER_FIELD}, topN))


from util import word2vec
def trainWord2Vec():
    """
    训练word2vec词向量
    :return:
    """
    word2vec.train()

def getRelevantWords(testWord):
    """
    查看testWord的相关词汇，并且将不在词典中的词过滤掉
    :return:
    """
    tags = word2vec.getRelevantWords(testWord)
    print("过滤前:")
    print(tags)
    dw = jiebautil.DictWords()
    print("过滤后:")
    print(dw.filter(tags))

from util.whooshutil import WhooshUtil
def buildIndex():
    """
    创建全文检索索引
    :return:
    """
    wu = WhooshUtil(JSON_FILE, [QUESTION_FIELD, ANSWER_FIELD])
    wu.buildIndex()

def searchFullText(words):
    """
    基于全文检索的搜索
    :return:
    """
    wu = WhooshUtil(JSON_FILE, [QUESTION_FIELD, ANSWER_FIELD])
    wu.search(words)