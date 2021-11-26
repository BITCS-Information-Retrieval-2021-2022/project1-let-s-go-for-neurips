# 更新proxylist.txt中代理ip
import random
import requests
from lxml import etree
import os
import time


class getProxy:
    def __init__(self):
        self.url = 'https://www.kuaidaili.com/free/inha/'
        self.headers = self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0'}
        self.path = 'proxylist.txt'
        self.index = 0

    def getHtml(self):
        # rnd = random.randint(1,4000)
        rnd = self.index
        res = requests.get(self.url + str(rnd), headers=self.headers)
        res.encoding = 'utf-8'
        html = res.text
        self.parseHtml(html)

    def parseHtml(self, html):
        lst = []
        # todo
        parsehtml = etree.HTML(html)
        # print(parsehtml)
        #time.sleep(1)
        iplist = parsehtml.xpath('//*[@id="list"]/table/tbody/tr/td[1]')
        portlist = parsehtml.xpath('//*[@id="list"]/table/tbody/tr/td[2]')
        iflist = parsehtml.xpath('//*[@id="list"]/table/tbody/tr/td[3]')
        typelist = parsehtml.xpath('//*[@id="list"]/table/tbody/tr/td[4]')
        addrlist = parsehtml.xpath('//*[@id="list"]/table/tbody/tr/td[5]')
        num = 0
        for x, y, z, m, n in zip(iplist, portlist, addrlist, iflist, typelist):
            if x.text and y.text and z.text and m.text and n.text:
                if 's' not in n.text and 'S' not in n.text:
                    write_text = n.text + '://' + x.text + ':' + y.text + '\n'
                    self.writeComment(write_text)
                    num += 1
        # print('共采集代理：',num)

    def writeComment(self, lst):
        with open(self.path, 'a') as f:
            f.write(lst)

    # 主函数
    def main(self):
        # if os.path.exists(self.path):
        #     os.remove(self.path)
        for i in range(0,185):
            print(i)
            self.index = i + 1
            self.getHtml()

    def process_proxy(self):
        with open(self.path, 'r') as f:
            proxy = f.readlines()
        with open('proxylist_new.txt', 'a') as f:
            for p in proxy:
                print(p)
                f.write('HTTP://'+p)


if __name__ == '__main__':
    proxy = getProxy()
    proxy.main()
    #proxy.process_proxy()
