# 更新proxylist.txt中代理ip
import requests
from lxml import etree
import os


class getProxy:
    def __init__(self):
        self.url = ''
        self.headers = self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        self.path = 'proxylist.txt'

    def getHtml(self):
        res = requests.get(self.url, headers=self.headers)
        res.encoding = 'utf-8'
        html = res.text
        self.parseHtml(html)

    def parseHtml(self, html):
        lst = []
        # todo
        print('共采集代理：')

    def writeComment(self, lst):
         with open(self.path, 'a') as f:
             f.write(lst)

    # 主函数
    def main(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        self.getHtml()


if __name__ == '__main__':
    xici = getProxy()
    xici.main()
