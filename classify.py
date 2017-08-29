# coding=utf-8    
"""  
Created on 2015-12-30 @author: Eastmount   
"""

import time
import re
import os
import sys
import codecs
import shutil
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from util import jsonutil


''''' 
sklearn里面的TF-IDF主要用到了两个函数：CountVectorizer()和TfidfTransformer()。 
    CountVectorizer是通过fit_transform函数将文本中的词语转换为词频矩阵。 
    矩阵元素weight[i][j] 表示j词在第i个文本下的词频，即各个词语出现的次数。 
    通过get_feature_names()可看到所有文本的关键字，通过toarray()可看到词频矩阵的结果。 
    TfidfTransformer也有个fit_transform函数，它的作用是计算tf-idf值。 
'''

JSON_FILE = "./data/b.json"

def getTfIdf():


    # 读取预料 一行预料为一个文档
    corpus = jsonutil.IterCutField(JSON_FILE, {'title', 'answer'})


    # 将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()

    # 该类会统计每个词语的tf-idf权值
    transformer = TfidfTransformer()

    # 第一个fit_transform是计算tf-idf 第二个fit_transform是将文本转为词频矩阵
    idf = vectorizer.fit_transform(corpus)
    print(idf)
    tfidf = transformer.fit_transform(idf)

    # 获取词袋模型中的所有词语
    word = vectorizer.get_feature_names()

    # 将tf-idf矩阵抽取出来，元素w[i][j]表示j词在i类文本中的tf-idf权重
    weight = tfidf.toarray()

    resName = "./result/b.json.txt"
    result = codecs.open(resName, 'w', 'utf-8')
    for j in range(len(word)):
        result.write(word[j] + ' ')
    result.write('\r\n\r\n')

    sFilePath = "./result"
    # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
    # for i in range(len(weight)):
    #     print("--------Writing all the tf-idf in the", i, u" file into ", sFilePath + '/' + str.zfill(str(i),5) + '.txt'+ "--------")
    #     f = open(sFilePath + '/' + str.zfill(str(i), 5) + '.txt', 'w+')
    #     for j in range(len(word)):
    #         f.write(word[j] + "    " + str(weight[i][j]) + "\n")
    #     f.close()
    #
    # result.close()