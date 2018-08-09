
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


class StockData:

    def __init__(self,code):
        client = pymongo.MongoClient('localhost', 27017)
        table_stock = client['stock']
        daily_data = table_stock['daily']
        basic_data = table_stock['basics']
        self.daily=list(daily_data.find({'code' : code}).sort('date',pymongo.ASCENDING))
        self.basic=basic_data.find_one({'code':code})

    def _read32(self):
        res=[]
        for d in self.daily:
            try:
                client = pymongo.MongoClient('localhost', 27017)#增加大盘数据用于对照
                table_stock = client['stock']
                daily_data = table_stock['daily']
                b = daily_data.find_one({'code': '000001', 'date': d['date']})
                if b == None:
                    continue
                else:
                    res1d = [d['open'], d['close'], d['high'], d['low'], d['volume'], b['open'], b['close'], b['high'],
                             b['low'], b['volume']]
                    res.extend(res1d)
            except:
                print(d['date'])

        return numpy.array(res).dtype(float)





sd = StockData('000760')
r=sd._read32()
print(r.shape)

