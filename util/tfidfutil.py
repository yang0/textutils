import datetime
import math
import os
from util import jiebautil

IDF_FILE = "./tmp/idf.txt"






class IDFLoader(object):
    """
    加载IDF文件到内存
    """
    def __init__(self, idf_path=IDF_FILE):
        self.idf_path = idf_path
        self.idf_freq = {}     # idf
        self.mean_idf = 0.0    # 均值

    def load(self):       # 从文件中载入idf
        assert os.path.exists(IDF_FILE)
        cnt = len(self.idf_freq)
        if cnt == 0:
            with open(self.idf_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        word, freq = line.strip().split(' ')
                        cnt += 1
                    except Exception as e:
                        pass
                    self.idf_freq[word] = float(freq)

        print('Vocabularies loaded: %d' % cnt)
        self.mean_idf = sum(self.idf_freq.values()) / cnt


    def makeIdfFile(self, iterableString, rewrite=False):
        """
        创建IDF逆文档词频记录
        :param iterableString:
        :param rewrite: 如果idf文件存在是否要覆盖
        :return:
        """
        if os.path.exists(self.idf_path) and rewrite == False:
            self.load()
            return

        i = 0  # 总文档数
        for doc in iterableString:
            for x in doc.split():
                self.idf_freq[x] = self.idf_freq.get(x, 0) + 1
            if i % 1000 == 0:  # 每隔1000篇输出状态
                print('Documents processed: ', i, ', time: ',
                      datetime.datetime.now())
            i += 1

        with open(self.idf_path, 'w', encoding='utf-8') as f:
            for key, value in self.idf_freq.items():
                f.write(key + ' ' + str(math.log(i / value, 2)) + '\n')

        self.load()


class TFIDF(object):
    def __init__(self, idfLoader):
        self.idf_loader = idfLoader
        self.idf_freq = self.idf_loader.idf_freq
        self.mean_idf = self.idf_loader.mean_idf

    def extract_keywords(self, sentence, topK=5):    # 提取关键词
        # 分词
        seg_list = jiebautil.cutWords(sentence).split()

        freq = {}
        for w in seg_list:
            freq[w] = freq.get(w, 0.0) + 1.0  # 统计词频
        if '' in freq:
            del freq['']
        total = sum(freq.values())    # 总词数

        for k in freq:   # 计算 TF-IDF
            freq[k] *= self.idf_freq.get(k, self.mean_idf) / total

        tags = sorted(freq, key=freq.__getitem__, reverse=True)  # 排序

        if topK:   # 返回topK
            return tags[:topK]
        else:
            return tags


