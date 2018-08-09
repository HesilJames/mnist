import pymongo
from numpy import *



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

