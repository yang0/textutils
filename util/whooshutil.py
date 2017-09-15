# coding=utf-8
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer
import json
from util import configutil, jsonutil, jiebautil
from whoosh.query import *
from whoosh.qparser import MultifieldParser


class WhooshUtil():
    def __init__(self, jsonFile, fieldNames):
        self.jsonFile = jsonFile
        self.fieldNames = fieldNames

        # 使用结巴中文分词
        jiebautil.loadUserDicts()
        analyzer = ChineseAnalyzer()

        dic = {k:TEXT(stored=True, analyzer=analyzer) for k in fieldNames}

        # 创建schema, stored为True表示能够被检索
        self.schema = Schema(**dic)

        # schema = Schema(title=TEXT(stored=True, analyzer=analyzer), path=ID(stored=False),
        #                 content=TEXT(stored=True, analyzer=analyzer))

        # 存储schema信息至'indexdir'目录下
        self.indexdir = configutil.config["whoosh"]["index_dir"]
        if not os.path.exists(self.indexdir):
            os.mkdir(self.indexdir)





    # 按照schema定义信息，增加需要建立索引的文档
    # 注意：字符串格式需要为unicode格式
    def buildIndex(self):
        ix = create_in(self.indexdir, self.schema)
        writer = ix.writer()

        for r in jsonutil.iterJsonValue(self.jsonFile, self.fieldNames):
            writer.add_document(**r)

        # writer.add_document(title=u"第一篇文档", path=u"/a",
        #                     content=u"这是我们增加的第一篇文档")
        # writer.add_document(title=u"第二篇文档", path=u"/b",
        #                     content=u"第二篇文档也很interesting！")
        writer.commit()

        print("建立索引文件： %s" % self.indexdir)




    # 创建一个检索器
    def search(self, words):
        ix = open_dir(self.indexdir)
        searcher = ix.searcher()

        # And[Or[Term(title: 'aa'), Term(content:'aa')], Or[Term(title: 'bb'), Term(content:'bb')]]
        mparser = MultifieldParser(self.fieldNames, schema=self.schema)
        q = mparser.parse(" and ".join(words))

        # qs = []
        # # 搜索的关键词都必须得出现，出现在哪个字段都行
        # for w in words:
        #     qs.append(Or([Term(fn, w) for fn in self.fieldNames]))
        # q = And(qs)

        # 搜索第1页，每页20条
        results = searcher.search_page(q, 1, pagelen=3)
        # results = searcher.find("title", u"文档")

        # 检索出来的第一个结果，数据格式为dict{'title':.., 'content':...}
        # firstdoc = results[0].fields()
        #
        # # python2中，需要使用json来打印包含unicode的dict内容
        # jsondoc = json.dumps(firstdoc, ensure_ascii=False)
        #
        # print(jsondoc)  # 打印出检索出的文档全部内容
        # print(results[0].highlights("title"))  # 高亮标题中的检索词
        # print(results[0].score)  # bm25分数

        for r in results:
            doc = r.fields()
            print(doc.values())
            print("bm25分数： %f" % r.score)
            # for field in self.fieldNames:
            #     print(r.highlights(field))

        print("总共记录数： %i" % len(results))