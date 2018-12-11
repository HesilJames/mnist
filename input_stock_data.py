
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import pymongo
import gzip
import os

import tensorflow as tf

import numpy as np

DAYS = 64
ONEDAYCOUNT = 5
BIGLOWLEV = -0.03
SMALLLOWLEV = -0.005
SMALLHIGHLEV = 0.005
BIGHIGHLEV = 0.03

divisionRate = 0.85  #划分训练集和测试集的比例

class StockData:

    def __init__(self,code):
        client = pymongo.MongoClient('localhost', 27017)
        table_stock = client['stock']
        daily_data = table_stock['daily']
        basic_data = table_stock['basics']
        self.daily = list(daily_data.find({'code': code}).sort('date', pymongo.ASCENDING))
        self.big = list(daily_data.find({'code': '000001'}).sort('date', pymongo.ASCENDING))#增加大盘数据用于对照
        self.basic = basic_data.find_one({'code': code})
        self.trainCur = 0
        self.testCur = 0
        self.biggest = [0, 0, 0, 0] #统计最大最小用于归一化处理
        self.smallest = [0, 0, 0, 0]
        self.length=self.daily.__len__()
        for d in self.daily:
            if d['close'] > self.biggest[0]:
                self.biggest[0] = d['close']
            if d['close'] < self.smallest[0]:
                self.smallest[0] = d['close']
            if d['high'] > self.biggest[1]:
                self.biggest[1] = d['high']
            if d['high'] < self.smallest[1]:
                self.smallest[1] = d['high']
            if d['low'] > self.biggest[2]:
                self.biggest[2] = d['low']
            if d['low'] < self.smallest[2]:
                self.smallest[2] = d['low']
            if d['volume'] > self.biggest[3]:
                self.biggest[3] = d['volume']
            if d['volume'] < self.smallest[3]:
                self.smallest[3] = d['volume']




    def search_Big(self, dateStr ):
        for b in self.big:
            if b['date'] == dateStr:
                return b
        return None

    #对数据进行归一化处理
    def returnOne(self, col, number):
        length = self.biggest[col]-self.smallest[col]
        rate = (number-self.smallest[col])/length
        return rate


    def _read32(self):
        res = []
        label = []
        daylenth=self.daily.__len__()
        #print(daylenth)
        for i in range(DAYS, daylenth):
            res_low1=[]
            d=self.daily[i]
            for j in range(i-DAYS, i):
                tmp = self.daily[j]
                res_low1.extend([self.returnOne(0, tmp['close']), self.returnOne(1, tmp['high']),
                                 self.returnOne(2, tmp['low']), self.returnOne(3, tmp['volume'])])
            res.append(res_low1)
            b = self.search_Big(d['date'])
            if b == None:
                rate = (float(d['close'])-float(d['open']))/float(d['open'])
            else:
                    #涨跌数据减去大盘比率
                rate = ((float(d['close'])-float(d['open']))/float(d['open']))-((float(b['close'])-float(b['open']))/float(b['open']))
            if rate < BIGLOWLEV:
                label.append(np.array([0, 0, 0, 0, 1]))
            elif BIGLOWLEV < rate < SMALLLOWLEV:
                label.append(np.array([0, 0, 0, 1, 0]))
            elif SMALLLOWLEV < rate < SMALLHIGHLEV:
                label.append(np.array([0, 0, 1, 0, 0]))
            elif SMALLHIGHLEV < rate < BIGHIGHLEV:
                label.append(np.array([0, 1, 0, 0, 0]))
            else:
                 label.append(np.array([1, 0, 0, 0, 0]))

        self.stockData = np.array(res)
        self.lableData = np.array(label)
        length, width = np.shape(self.stockData)
        division = int(length*divisionRate)
        self.trainData = self.stockData[0: division]
        self.trainLabel = self.lableData[0: division]
        self.testData = self.stockData[division: length]
        self.testLabel = self.lableData[division: length]

        return np.array(res), np.array(label)

    def net_batch(self, which, num):
        if which == 'train':
            if (self.trainCur + num) > self.trainLabel.__len__():
                res = (np.append(self.trainData[self.trainCur: self.trainLabel.__len__()],
                                 self.trainData[0: self.trainCur+num - self.trainLabel.__len__()], axis=0),
                       np.append(self.trainLabel[self.trainCur: self.trainLabel.__len__()],
                                 self.trainLabel[0: self.trainCur + num - self.trainLabel.__len__()], axis=0))
                self.trainCur = self.trainCur + num - self.trainLabel.__len__()
            else:
                res = (self.trainData[self.trainCur: self.trainCur + num],
                       self.trainLabel[self.trainCur:self.trainCur + num])
                self.trainCur = self.trainCur + num
            return res

        if which == 'test':
            if (self.testCur + num) > self.testLabel.__len__():
                res = (np.append(self.testData[self.testCur: self.testLabel.__len__()],
                                 self.testData[0: self.testCur + num - self.testLabel.__len__()], axis=0),
                       np.append(self.testLabel[self.testCur: self.testLabel.__len__()],
                                 self.testLabel[0: self.testCur + num - self.testLabel.__len__()], axis=0))
                self.testCur = self.testCur + num - self.testLabel.__len__()
            else:
                res = (self.testData[self.testCur: self.testCur + num],
                       self.testLabel[self.testCur: self.testCur + num])
                self.testCur = self.testCur + num
            return res

        # label=np.zeros(shape=(-1, ONEDAYCOUNT), dtype=float)
        #
        # for d in self.daily:
        #     try:
        #         b = self.search_Big(d['date'])
        #         if b == None:
        #             continue
        #         else:
        #             res1d = [d['open'], d['close'], d['high'], d['low'], d['volume']]
        #             #涨跌数据减去大盘比率
        #             rate=((float(d['close'])-float(d['open']))/float(d['open']))-((float(b['close'])-float(b['open']))/float(b['open']))
        #             if rate<-3:
        #                 label.append(0)
        #             elif -3<rate<-1:
        #                 label.append(1)
        #             elif -1<rate<1:
        #                 label.append(2)
        #             elif 1<rate<3:
        #                 label.append(3)
        #             else:
        #                 label.append(4)
        #             res.extend(res1d)
        #     except:
        #         print(d['date'])
        # res_reshape=[]
        # m=res.__len__()
        # res=list(res)
        # for i in range(0,m-DAYS*ONEDAYCOUNT,ONEDAYCOUNT):
        #     res_reshape.append(res[i:i+(DAYS*ONEDAYCOUNT)])
        # label=label[DAYS:]
        # #股票基本数据附在数组最尾
        # return np.array(res_reshape), np.array(label)

'''
sd = StockData('000760')
r, l = sd._read32()
print(r.shape)
print(l.shape)
'''

#print(l)


