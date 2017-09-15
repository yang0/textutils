#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-08-23 07:38:12
# Project: b


#这个文件拷贝到浏览器pyspider窗口中使用


from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        """
        抓取宝宝树的问答信息
        :return:
        """
        self.crawl('http://www.babytree.com/ask/myqa__view~mlist,tab~D,age_id~1,pg~1', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.pagejump > a').items():
            self.crawl(each.attr.href, callback=self.index_page)

        for each in response.doc('.list-item').items():
            answerNum = int(each('.list-answer').html()[:-2])
            if answerNum > 0:
                self.crawl(each("a").attr.href, callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('[itemprop="title"]').text(),
            "answer": response.doc('[itemprop="content"]').text(),
        }
