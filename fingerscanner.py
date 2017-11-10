#!/usr/bin/python
#coding:utf-8

'''
Author:Leo
Date:2017/11/9

A simple scanner about the Web finger info detection

Refer:seaii fenghuangscaner
'''


import requests
import threading
import Queue
import hashlib
import json
import re
import sys
import time
#import socks
#import socket

reload(sys)
sys.setdefaultencoding('utf-8')

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, compress',
           'Cache-Control': 'max-age=0',
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0',
           'Upgrade-Insecure-Requests': '1'
           }
S=requests.session()
S.headers.update(headers)

#socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', port)
#socket.socket = socks.socksocket

class cmsRecognize(object):

    def __init__(self, url, threads=50):#默认线程50
        self.url = url
        self.filePath = './webfinger.json'
        self.q = Queue.Queue()#定义队列
        self.threads = threads
        self.isKnown = False
        self.resaults=['']

    #web请求
    def request(self, url):
        global S
        try:
            r = S.get(url, timeout=10)
        except requests.exceptions.Timeout as e:
            print(e)
            return False
        except requests.exceptions.MissingSchema as e:
            print(e)
            return False
        except requests.exceptions.RequestException as e:
            print(e)
            return False
        return r.text if r.status_code == 200 else False

    #获取文件的md5值
    def getMd5Info(self, path):
        url = self.url + path
        response = self.request(url)
        if response:
            #print url,time.ctime()
            md5 = hashlib.md5()
            md5.update(response.encode('utf-8'))
            return md5.hexdigest()
        return False

    #获取页面内容
    def getContent(self, path):
        url = self.url + path
        response = self.request(url)
        if response:
            #print url,time.ctime()
            return response
        return False

    #json解析
    def readFile(self):
        filename = self.filePath
        with open(filename, 'r') as f:
            content=f.read().decode('gbk')
        finger=json.loads(content)
        return finger

    #获取指纹特征
    def getFeature(self):
        for line in self.readFile():
            #print line
            self.q.put(line)
    #对比指纹特征
    def compareFeature(self):
        while not self.q.empty():
            content = self.q.get()
            if  content['md5']!='':
                 md5=''
                 md5=str(self.getMd5Info(content['url']))
                 if md5:
                     if re.search(content['md5'],md5):
                         print('[*]Based on feature:', content['name'],content['url'])
                         self.isKnown=True
                         self.resaults.append(content['name'])
            elif content['md5']=='':
                text=self.getContent(content['url'])
                if text:
                    try:
                        if re.search(content['re'],text):
                            print('[*]Based on feature:', content['name'],content['url'])
                            self.isKnown=True
                            self.resaults.append(content['name'])
                    except:
                        continue
            else:
                print content
                return False

    def run(self):
        self.getFeature()
        for i in range(self.threads):
            t = threading.Thread(target=self.compareFeature)
            t.setDaemon(True)
            t.start()

        self.q.join()

        if not self.isKnown:
            print('[-]Based on feature: Unknown')
        else:
            print('[+]This is the resaults : ')
            for i in resaults:
                print i

if __name__ == '__main__':
    cms = cmsRecognize('http://www.wordpress.org',threads=50)
    cms.run()
