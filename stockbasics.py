import pymongo
import json
import tushare as ts
import datetime
import pandas as pd
import numpy as np

STARTYEAR=2000
ENDYEAR=2018

def str2Date(str):
    return datetime.datetime.strptime(str,"%Y-%m-%d")

def get_day_nday_ago(date,n):
    return date+datetime.timedelta(days=-n)

def get_stock_basics():
    client = pymongo.MongoClient('localhost', 27017)
    table_stock = client['stock']
    sheet_basics = table_stock['basics']
    df = ts.get_stock_basics()
    codearray=df.to_xarray().code
    jsonres = json.loads(df.to_json(orient='records'))
    for i in range(0,jsonres.__len__()):
        jsonres[i]['code']=change_int_code(int(codearray[i]))
    for detail in jsonres:
        findRes=sheet_basics.find({'code':detail['code']})
        if findRes.count()==0:
            sheet_basics.insert_one(detail)
        else:
            print(detail)

def change_int_code(intVar):
    strVar=str(intVar)
    while strVar.__len__()<6:
        strVar='0'+strVar
    return strVar


def get_stock_code(year,month):                           #暂时停用此方法
    client = pymongo.MongoClient('localhost', 27017)
    table_stock = client['stock']
    sheet_basics = table_stock['basics']
    tf=ts.get_cashflow_data(year, month)
    jsonres = json.loads(tf.to_json(orient='records'))
    for detail in jsonres:
        sheet_basics.update_one({'name':detail['name']},{'$set':{'code':detail['code']}})

def get_all_stock_code():
    client = pymongo.MongoClient('localhost', 27017)
    table_stock = client['stock']
    sheet_basics = table_stock['basics']
    stocks=sheet_basics.find()  #{'code':{'$ne':None}}
    res=[]
    for s in stocks:
        try:
            res.append(s['code'])
        except:
            continue
    return  res

def get_all_stock_code_from_daily():
    client = pymongo.MongoClient('localhost', 27017)
    table_stock = client['stock']
    sheet_daily = table_stock['daily']
    return sheet_daily.distinct('code')


def getDailyData(code):
    print('Processing with code:'+code)
    client = pymongo.MongoClient('localhost', 27017)
    table_stock = client['stock']
    sheet_daily=table_stock['daily']
    res=ts.get_k_data(code,'1990-01-01','2018-7-17')
    jsonres=json.loads(res.to_json(orient='records'))
    for j in jsonres:
        sheet_daily.insert_one(j)
    print('finish processing code:'+code)




def getDailyData(code,starttime,endtime=datetime.datetime.today()):
    client = pymongo.MongoClient('localhost', 27017)
    table_stock = client['stock']
    sheet_daily=table_stock['daily']
    ndays_ago=starttime
    str_ndays_ago=ndays_ago.strftime("%Y-%m-%d")
    str_end_date=endtime.strftime("%Y-%m-%d")
    #sheet_daily.update()
    sqlres = sheet_daily.find({'$and':[{'date':{'$gte': str_ndays_ago}},{'code':code},{'date':{'$lt':str_end_date}}]})
    resArray=[]
    for s in sqlres:
        resArray.append(float(s['close']))
    resPD=pd.DataFrame(resArray)

#获取所有基本面数据
def get_basic_datas(data_kind):#datakind 为debtpaying,growth,operation,profit,report
    client = pymongo.MongoClient('localhost', 27017)
    table_stock = client['stock']
    sheet=table_stock[data_kind]
    for year in range(STARTYEAR,ENDYEAR+1):
        try:
            for season in range(1, 5):
                print('getting ' + datakind + ' data at year:' + str(year) + " season:" + str(season))
                if data_kind == 'debtpaying':
                    tf = ts.get_debtpaying_data(year, season)
                elif data_kind == 'growth':
                    tf = ts.get_growth_data(year, season)
                elif data_kind == 'operation':
                    tf = ts.get_operation_data(year, season)
                elif data_kind == 'profit':
                    tf = ts.get_profit_data(year, season)
                elif data_kind == 'report':
                    tf = ts.get_report_data(year, season)
                else:
                    print('Not available data type of data_kind!')
                    return
                jsonres = json.loads(tf.to_json(orient='records'))
                for j in jsonres:
                    sheet.insert_one(j)
        except:  #数据缺失，tushare接口会报网络错误
            print('the year: '+str(year)+' lost data will begin next year')
            continue


#datakinds=['debtpaying','growth','operation','profit','report']
# datakinds=['growth','operation','profit','report']
# for datakind in datakinds:
#     print('start getting '+datakind+'....')
#     get_basic_datas(datakind)

#test_get_stock_code()
#allStockCode=get_all_stock_code()
#print(allStockCode)
#print(allStockCode)
#get_stock_basics()
