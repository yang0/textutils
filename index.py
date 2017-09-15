import argparse, json
from vallleyparser.vallleyparser import runApp as runValleyParser
import demo
import subprocess

# 提取每个问答中的关键词， 存入mongodb, tf-idf
# 根据关键词进行文本聚类, k-means

# 建立word2vec，演示词汇相似度
# 计算句子的相似度 方式待定

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='选择一个参数运行相应功能')
    parser.add_argument('--parse', '-p', action='store_true', help='处理对话json文件')
    parser.add_argument('--pyspider', '-r', action='store_true', help='启动爬虫pyspider')
    parser.add_argument('--insertMongo', '-i' , metavar=('db', 'collection'), nargs=2 , help='将爬取的json文件录入到mongodb')
    parser.add_argument('--tfIdf', '-t',  metavar='topN', nargs=1, type=int, help='从json文件每一行都提取topN个关键词(自己实现的idf)')
    parser.add_argument('--jiebaKeywords', '-j', metavar='topN', nargs=1, type=int, help='从json文件每一行都提取topN个关键词(jieba方案，首选)')
    parser.add_argument('--cutWords', '-c', metavar='句子', nargs=1, help='测试分词')
    parser.add_argument('--findk', '-k', metavar=('最多可能的分类数', '每个文本提取的关键词数'), nargs=2, type=int, help='对多个文本预估最合理的分类数量')
    parser.add_argument('--classify', '-l', metavar='类目数量', nargs=1, type=int, help='对文本分类')
    parser.add_argument('--search', '-s', metavar='关键词', nargs='*',  help='按关键词搜索')
    parser.add_argument('--keywords','-w', metavar='int', nargs=1, type=int, help='遍历所有文本取得topN个关键词')
    parser.add_argument('--saveCutFile', action='store_true', help='将json文件中的字段分词后保存到一个文本文件中，便于word2vec使用')
    parser.add_argument('--word2vecTrain', '-wt', action='store_true', help='将json相应字段训练成word2vec词向量')
    parser.add_argument('--getRelevantWords', '-wr', metavar='关键词', nargs=1,  help='查看某个关键词的相关词汇，并且过滤掉不在jieba词典中的词，前提是word2vec已完成训练')
    parser.add_argument('--buildIndex', '-b', action='store_true', help='创建全文检索索引')
    parser.add_argument('--searchFullText', '-sf', metavar='关键词', nargs="*", help='基于全文检索的搜索')
    parser.add_argument('--buildSimModel', '-ti', action='store_true', help='构建tf-idf, lis等模型')
    parser.add_argument('--querySimString', '-qs', metavar='句子', nargs=1, help='搜索相似度最高的句子')
    parser.add_argument('--bm25Search', '-bs', metavar='句子', nargs=1, help='基于bm25算法搜索相似度最高的句子，实测效果没有ifidf+lsi好')
    parser.add_argument('--snownlpDemo', '-sd', action='store_true', help='演示snowlp工具包情感分析，汉字转拼音等功能')
    parser.add_argument('--pdfDemo', '-pdf', action='store_true', help='演示pdf转换成图片，再从图片转换成pdf')

    args = parser.parse_args()

    if args.pyspider:
        subprocess.call('pyspider')
    elif args.parse:
        runValleyParser()
    elif args.insertMongo:
        demo.insertMongo(args.insertMongo[0], args.insertMongo[1])
    elif args.tfIdf:
        demo.getTopKeyWords(args.tfIdf[0])
    elif args.jiebaKeywords:
        demo.getTopKeyWordsByJieba(args.jiebaKeywords[0])
    elif args.cutWords:
        demo.cutWords(args.cutWords[0])
    elif args.findk:
        demo.findK(args.findk[0], args.findk[1])
    elif args.classify:
        demo.classify(args.classify[0])
    elif args.search:
        demo.search(args.search)
    elif args.keywords:
        demo.getKeywords(args.keywords[0])
    elif args.saveCutFile:
        demo.saveCutFile()
    elif args.word2vecTrain:
        demo.trainWord2Vec()
    elif args.getRelevantWords:
        demo.getRelevantWords(args.getRelevantWords[0])
    elif args.buildIndex:
        demo.buildIndex()
    elif args.searchFullText:
        demo.searchFullText(args.searchFullText)
    elif args.buildSimModel:
        demo.buildSimModel()
    elif args.querySimString:
        demo.querySimString(args.querySimString[0])
    elif args.bm25Search:
        demo.bm25Search(args.bm25Search[0])
    elif args.snownlpDemo:
        demo.snownlpDemo()
    elif args.pdfDemo:
        demo.pdfDemo()
    else:
        parser.print_help()




