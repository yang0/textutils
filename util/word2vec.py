import multiprocessing
import os
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from util import configutil

WORD2VEC_INDEX = 2
#计算cpu有几核
CPU_COUNT = multiprocessing.cpu_count()


WORDS_CUT_FILE = configutil.config["json"]["cut_file"]
VOCABULARY_BIN_FILE = configutil.config["word2vec"]["bin_file"]



def train():
    """
    将json字段训练词向量
    :return:
    """



    sentences = LineSentence(WORDS_CUT_FILE)
    # size向量的维度，min_count忽略所有总词频低于这个值的词, 在一个句子内，目标词与预测词之间的最大距离
    model = Word2Vec(sentences, sg=0, size=800, window=5, min_count=5, negative=3, sample=0.001, hs=1, workers=CPU_COUNT)

    # # 建立词表
    # model.build_vocab(sentences)
    #
    # # 建立词向量
    # token_count = sum([len(sentence) for sentence in sentences])
    # model.train(sentences, total_examples = token_count,epochs = model.iter)

    model.save(VOCABULARY_BIN_FILE)




def getRelevantWords(test_word):
    """
    取得test_word的20个相关词汇
    :param test_word:
    :return:
    """
    model = Word2Vec.load(VOCABULARY_BIN_FILE)
    # print("# %s %s" % (model, VOCABULARY_BIN_FILE))

    y2 = model.wv.most_similar(positive=[test_word], negative=[], topn=20)
    return [item[0] for item in y2]


