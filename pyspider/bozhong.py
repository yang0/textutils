#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-08-28 16:57:29
# Project: bozhong

from pyspider.libs.base_handler import *
import datetime


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://bbs.bozhong.com/', callback=self.index_page)

    @config(priority=2)
    def index_page(self, response):
        i = 0
        for each in response.doc('.map-item').items():
            if i < 2:
                for link in each('a').items():
                    self.crawl(link.attr.href, callback=self.list_page)
            i += 1

    @config(priority=2)
    def list_page(self, response):
        for each in response.doc('.tagList a').items():
            a = self.crawl(each.attr.href, callback=self.sublist_page)
            print(a)

    @config(age=2 * 24 * 60 * 60)
    def sublist_page(self, response):

        for tb in response.doc('form[name=moderate] tbody').items():
            count = tb('a.xi2').text()
            if count == "":
                continue

            count = int(count)
            if count > 19:
                count = 19

            if count > 0:
                self.crawl(tb('a.xst').attr.href, callback=self.detail_page, itag=count)

        # 抓取所有的帖子更新日期，如果今天昨天没有更新的，那么就不要翻页了
        # twoDaysAgo = datetime.datetime.today() - datetime.timedelta(days=2)
        # twoDaysAgo = twoDaysAgo.timestamp()
        # dates = [e.text() for e in response.doc('.thread_dateline').items()]
        # dates = [datetime.datetime.strptime(a, "%Y-%m-%d").timestamp() for a in dates]
        # shouldCrawl = False
        # for d in dates:
        #     if d > twoDaysAgo:
        #         shouldCrawl = True
        #         break
        #
        # if shouldCrawl:
        for each in response.doc('.pg a').items():
            self.crawl(each.attr.href, callback=self.sublist_page)

    @config(priority=1)
    def detail_page(self, response):
        title = response.doc('.ts-title').text()
        content = response.doc('td[first="1"]').remove('i').text()
        if title == "" or content == "":
            return
        postList = response.doc('.post_list').items()
        replies = []
        for post in postList:
            userName = post('.user_name').text()
            if userName == "":
                continue
            reply = post('td[first="0"]').remove('dive').text()
            replies.append(userName + ":" + reply)

        if len(replies) == 0:
            return

        tmpStr = response.doc('.ts').text()

        return {
            "url": response.url,
            "author": response.doc(".auth_info_bar").text(),
            "category": tmpStr[tmpStr.find('[') + 1: tmpStr.find(']')],
            "title": title,
            "content": content,
            "replies": replies
        }
