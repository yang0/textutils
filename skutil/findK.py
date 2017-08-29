import os
import jieba
import jieba.analyse
import numpy as np
from sklearn.cluster import KMeans
from pylab import *



# 提取训练集中文本的关键字
def getTags(iterString, keywordsNum) :
    """

    :param iterString:
    :param keywordsNum:
    :return: wordDic: 保存着所有关键词，每个关键词一个流水号，wordslist: 一个文档的关键词一条记录 len(wordslist)=文档数量
    """

    wordDic, wordslist = {}, []
    # os.listdir() 提取相应路径下的文件名
    for s in iterString:
        # extract_tags() 函数提取关键字
        text = ' '.join(jieba.analyse.extract_tags(s, topK=keywordsNum))
        words = text.split()
        # 将当前文本关键字放入总的关键字列表中
        wordslist.append(words)
        # 将当前文本关键字放入关键字字典中
        for word in words :
            wordDic[word] = 0
    # 遍历官架子字典，为每一个关键字取定一个字段值，即列号存入字典
    for (word, seqNo) in zip(wordDic, range(len(wordDic))) :
        wordDic[word] = seqNo
    return wordDic, wordslist

def getMatrix(wordDic, wordslist) :
    """
    假设10个文档，20个关键词，那么构建一个【10，20】维度的数组，初始化赋值：1
    :param wordDic:
    :param wordslist:
    :return:
    """
    # 取定第一维为文本数，第二维为关键字数量的零矩阵
    wordMatrix = np.zeros([len(wordslist), len(wordDic)])
    # 第i个文本包含第j个词，则wordMatrix[i, j] = 1,构造01矩阵
    for (i, words) in zip(range(len(wordslist)), wordslist) :
        for word in words :
            wordMatrix[i, wordDic[word]] = 1
    # 返回01矩阵
    return wordMatrix


def findk(iterString, topK=10, keywordsNum=10):
    """
    寻找最适合的K值（分类数量），图中明显的拐点就是合适的K值
    :param iterString: 输入的字符串
    :param topK: 封顶的分类数量
    :param keywordsNum: 每个字符串提取10个关键词（使用jieba默认的tf-idf提取）
    :return:
    """

    # 提取文本关键字列表与关键词字典
    wordDic, wordslist = getTags(iterString, keywordsNum)

    # 构造关键词01矩阵
    wordMatrix = getMatrix(wordDic, wordslist)

    # n 表示聚类数量K的封顶值
    n, distance = topK, []
    for i in range(1, n) :
        # 初始化最小距离为 -1
        minDis = -1
        # 跑10次Kmeans以保证取得的是全局最优解（10可以更大）
        for j in range(10) :
            # 调用sklearn的kmeans类
            kmeans = KMeans(n_clusters = i).fit(wordMatrix)
            # centers 表示每个样本对应的聚类中心点
            centers = np.array([kmeans.cluster_centers_[k] for k in kmeans.labels_])
            # 计算当前Kmeans结果的距离，取欧式距离但没有开方
            dis = ((wordMatrix - centers) ** 2).sum()
            # 更新最小值
            minDis = dis if minDis < 0 else min(minDis, dis)
        # 将相应的k值存入distance列表
        distance.append(minDis)
    # 绘图
    plot(range(1, n), distance)
    # 绘制网格
    grid()
    show()

