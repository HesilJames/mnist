
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import pymongo
import gzip
import os

import tensorflow.python.platform

import numpy
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

DAYS=80
ONEDAYCOUNT=5

class StockData:

    def __init__(self,code):
        client = pymongo.MongoClient('localhost', 27017)
        table_stock = client['stock']
        daily_data = table_stock['daily']
        basic_data = table_stock['basics']
        self.daily = list(daily_data.find({'code' : code}).sort('date',pymongo.ASCENDING))
        self.big = list(daily_data.find({'code' : '000001'}).sort('date',pymongo.ASCENDING))#增加大盘数据用于对照
        self.basic = basic_data.find_one({'code' : code})

    def search_Big(self, dateStr ):
        for b in self.big:
            if b['date'] == dateStr:
                return b
        return None


    def _read32(self):
        res=[]
        label=[]
        for d in self.daily:
            try:
                b = self.search_Big(d['date'])
                if b == None:
                    continue
                else:
                    res1d = [d['open'], d['close'], d['high'], d['low'], d['volume']]
                    #涨跌数据减去大盘比率
                    rate=((float(d['close'])-float(d['open']))/float(d['open']))-((float(b['close'])-float(b['open']))/float(b['open']))
                    if rate<-3:
                        label.append(-2)
                    elif rate<0:
                        label.append(-1)
                    elif rate<3:
                        label.append(1)
                    else:
                        label.append(2)
                    res.extend(res1d)
            except:
                print(d['date'])
        res_reshape=[]
        m=res.__len__()
        res=list(res)
        for i in range(0,m-DAYS*ONEDAYCOUNT,ONEDAYCOUNT):
            res_reshape.append(res[i:i+(DAYS*ONEDAYCOUNT)])
        label=label[DAYS:]
        return numpy.array(res_reshape) , label


sd = StockData('000760')
r,l=sd._read32()

