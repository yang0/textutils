import jieba.posseg as pseg
import codecs
from gensim import corpora
from gensim.summarization import bm25
import os
import re
from util import jsonutil, configutil, jiebautil
from util.linereader import LineReader
import json

DICTIONARY_PATH = configutil.config["sim"]["dic_path"]

def buildModel(jsonFile, fieldNames, query_str):
    # iterable 不能循环两次，所以创建两个变量
    t1 = jsonutil.iterCutFieldList(jsonFile, fieldNames)
    t2 = jsonutil.iterCutFieldList(jsonFile, fieldNames)

    # 建立单词索引字典
    dictionary = corpora.Dictionary(t1)
    dictionary.save(DICTIONARY_PATH)

    # 建立词袋模型.将词汇表示的文本，转换成用id表示
    corpus = [dictionary.doc2bow(text) for text in t2]
    print("词袋: %i " % len(corpus))

    bm25Model = bm25.BM25(corpus)


    # print("bm25 idf lens: %i " %len(bm25Model.f))

    average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())

    query = jiebautil.cutWords(query_str).split()
    query_bow = dictionary.doc2bow(query)

    scores = bm25Model.get_scores(query_bow, average_idf)
    # i = scores.index(max(scores))

    lineRead = LineReader(jsonFile)
    for i in range(5):
        score = max(scores)
        lineNum = scores.index(score) + 1
        s = lineRead.load(lineNum)
        j = json.loads(s)
        print(jsonutil.recursive_get(j, fieldNames[0]))

        del scores[lineNum-1]