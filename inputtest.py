from input_stock_data import StockData
import numpy as np

'''
stock = StockData('000636')
stockD, stockL = stock._read32()
stock.trainCur = 4100
num = 100
print(stock.trainData[stock.trainCur: stock.trainLabel.__len__()])
res = (np.append(stock.trainData[stock.trainCur: stock.trainLabel.__len__()],
                      stock.trainData[0: (stock.trainCur+num - stock.trainLabel.__len__())], axis=0))
print(res.shape)'''
a = np.array(range(16)).reshape([4, 4])
print(a)
print(np.max(a))
print(np.where(a > 6))