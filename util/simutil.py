from gensim import corpora, models, similarities
import logging
from util import jsonutil, configutil, jiebautil
from  util.linereader import LineReader
import itertools
from gensim.similarities import Similarity

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

DICTIONARY_PATH = configutil.config["sim"]["dic_path"]
TFIDF_MODEL = configutil.config["sim"]["tfidf_path"]
LSI_MODEL = configutil.config["sim"]["lsi_path"]
CORPUS_PATH = configutil.config["sim"]["corpus_path"]
INDEX_PATH = configutil.config["sim"]["index_path"]

def buildModel(jsonFile, fieldNames):
    """
    构建词-id映射字典，tf-idf模型
    :param jsonFile:
    :param fieldNames:
    :return:
    """

    # iterable 不能循环两次，所以创建两个变量
    t1 = jsonutil.iterCutFieldList(jsonFile, fieldNames)
    t2 = jsonutil.iterCutFieldList(jsonFile, fieldNames)


    # 建立单词索引字典
    dictionary = corpora.Dictionary(t1)
    dictionary.save(DICTIONARY_PATH)


    # 建立词袋模型.将词汇表示的文本，转换成用id表示
    corpus = [dictionary.doc2bow(text) for text in t2]
    print("词袋: %i " % len(corpus))
    # corpora.MmCorpus.serialize(CORPUS_PATH, corpus)


    # 其中TF表示词频，即一个词在这篇文本中出现的频率；IDF表示逆文档频率，即一个词在所有文本中出现的频率倒数。
    # 因此，一个词在某文本中出现的越多，在其他文本中出现的越少，则这个词能很好地反映这篇文本的内容，权重就越大
    tfidf = models.TfidfModel(corpus)
    # tfidf.save(TFIDF_MODEL)

    #这里我们拍脑门决定训练topic数量为10的LSI模型：
    # LSI是概率主题模型的一种，另一种常见的是LDA，核心思想是：每篇文本中有多个概率分布不同的主题；
    # 每个主题中都包含所有已知词，但是这些词在不同主题中的概率分布不同。LSI通过奇异值分解的方法计算出
    # 文本中各个主题的概率分布，严格的数学证明需要看相关论文。假设有5个主题，那么通过LSI模型，文本向量
    # 就可以降到5维，每个分量表示对应主题的权重。
    corpus_tfidf = tfidf[corpus]
    print("tfidf文档数 %i" % len(corpus_tfidf))

    # print(corpus_tfidf)

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
    lsi.save(LSI_MODEL)

    lsi_vector = lsi[corpus_tfidf]
    index = similarities.MatrixSimilarity(lsi_vector)
    index.save(INDEX_PATH)


    # index = similarities.MatrixSimilarity(lsi[corpus])
import json
def querySimString(jsonFile, fieldName, sentence):
    """
    取得和sentence相似的句子
    :param sentence:
    :return:
    """
    dictionary = corpora.Dictionary.load(DICTIONARY_PATH)
    lsi = models.LsiModel.load(LSI_MODEL, mmap='r')

    query = jiebautil.cutWords(sentence).split()
    #将词转换成id
    query_bow = dictionary.doc2bow(query)


    query_lsi = lsi[query_bow]

    index = similarities.MatrixSimilarity.load(INDEX_PATH)
    sims = index[query_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    for e in sims[:5]:
        lineRead = LineReader(jsonFile)
        s = lineRead.load(e[0]+1)
        j = json.loads(s)
        print(jsonutil.recursive_get(j, fieldName))









