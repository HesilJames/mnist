import tensorflow as tf
import numpy as np
from input_stock_data import StockData

stock = StockData('000636')
stockData, stockLabel = stock._read32()
print('data loading complete!')
length, width = stockData.shape
division=int(length*2/3)
trainData=stockData[0:division]
trainLabel=stockLabel[0:division]
testData=stockData[division:length]
testLable=stockLabel[division:length]
print(stockData.shape)
print(stockLabel.shape)

trainCur=0
testCur=0

def next_batch(which,num):
    global trainCur
    global testCur
    if which == 'train':
        res = (trainData[trainCur: trainCur + num], trainLabel[trainCur:trainCur + num])
        trainCur = trainCur + num
        return res
    if which == 'test':
        res = (testData[testCur: testCur + num], testLable[testCur:testCur + num])
        testCur = testCur + num
        return res




def add_layer(inputs, in_size, out_size, activation_function=None):
    Weights = tf.Variable(tf.random_normal([in_size, out_size]))
    biases = tf.constant(0.1, shape=[1, out_size])
    Wx_plus_b = tf.matmul(inputs, Weights)+biases
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b)
    return outputs

def compute_accuracy(v_xs,v_ys):
    global prediction
    y_pre=sess.run(prediction, feed_dict={xs:v_xs})
    correct_prediction=tf.equal(tf.argmax(y_pre,1),tf.argmax(v_ys,1))
    accuracy=tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
    result=sess.run(accuracy, feed_dict={xs:v_xs,ys:v_ys})
    return  result

xs=tf.placeholder(tf.float32, [None, 256])
ys=tf.placeholder(tf.float32, [None, 5])

#add output layer
prediction=add_layer(xs, 256, 5, activation_function=tf.nn.softmax)
cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys * tf.log(prediction),reduction_indices=[1]))
train_step=tf.train.GradientDescentOptimizer(0.1).minimize(cross_entropy)

#error between prediction and real data

sess = tf.Session()
init = tf.global_variables_initializer()
sess.run(init)

for i in range(500):
    batch_xs, batch_ys=next_batch('train', 50)
    sess.run(train_step, feed_dict={xs:batch_xs, ys:batch_ys})
    if i % 50 == 0:
        print(compute_accuracy(testData, testLable))