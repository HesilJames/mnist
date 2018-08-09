
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


sd = StockData('000760')
print(sd.basic['name'])
print(sd.daily.__len__())

