import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def jieba_tokenize(text):
    return jieba.lcut(text)

def classify(iterString, clusterNum=5):
    tfidf_vectorizer = TfidfVectorizer(tokenizer=jieba_tokenize, \
                                       lowercase=False)
    '''
    tokenizer: 指定分词函数
    lowercase: 在分词之前将所有的文本转换成小写，因为涉及到中文文本处理，
    所以最好是False
    '''

    # 需要进行聚类的文本集
    tfidf_matrix = tfidf_vectorizer.fit_transform(iterString)

    km_cluster = KMeans(n_clusters=clusterNum, max_iter=300, n_init=40, \
                        init='k-means++', n_jobs=-1)
    '''
    n_clusters: 指定K的值
    max_iter: 对于单次初始值计算的最大迭代次数
    n_init: 重新选择初始值的次数
    init: 制定初始值选择的算法
    n_jobs: 进程个数，为-1的时候是指默认跑满CPU
    注意，这个对于单个初始值的计算始终只会使用单进程计算，
    并行计算只是针对与不同初始值的计算。比如n_init=10，n_jobs=40,
    服务器上面有20个CPU可以开40个进程，最终只会开10个进程
    '''
    # 返回各自文本的所被分配到的类索引
    result = km_cluster.fit_predict(tfidf_matrix)

    classifyList = []
    for i in range(clusterNum):
        # 获取每个分类对应的index值，也就是iterString的索引号
        indexList = [index for index, value in enumerate(result) if value == i]
        classifyList.append(indexList)

    return classifyList
