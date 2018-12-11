import tensorflow as tf
import input_data
import numpy as np
import matplotlib.pyplot as plt
from input_stock_data import StockData
import stockbasics

VALIDPROB = 0.73



def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')

def plotnumber(x):
    f, a = plt.subplots(1, 1, figsize=(1, 1))
    a.imshow(np.reshape(x, (28, 28)))
    plt.show()

def pre_stock(stock, index=0):
    yesterday_data = stock.testData[stock.testData.__len__()-index-1:stock.testData.__len__()-index]
    yesterday_y=stock.testLabel[stock.testData.__len__()-index-1:stock.testData.__len__()-index]
    #print(yesterday_data)
    #print(yesterday_data.shape)
    x = tf.placeholder("float", [None, 256])
    W = tf.Variable(tf.zeros([256, 5]))
    b = tf.Variable(tf.zeros([5]))
    y = tf.nn.softmax(tf.matmul(x, W) + b)
    y_ = tf.placeholder("float", [None, 5])
    #conv1 layer
    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])
    x_image = tf.reshape(x, [-1, 16, 16, 1])
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)   #output 16*16*32
    h_pool1 = max_pool_2x2(h_conv1)                            #output 8*8*32
    #conv2 layer
    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([4 * 4 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 4 * 4 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    keep_prob = tf.placeholder("float")
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
    W_fc2 = weight_variable([1024, 5])
    b_fc2 = bias_variable([5])
    y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
    cross_entropy = -tf.reduce_sum(y_ * tf.log(y_conv))
    train_step = tf.train.AdamOptimizer(1e-5).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())
    for i in range(100):
        batch_xs, batch_ys = stock.net_batch(which='train', num=100)
        train_step.run(feed_dict={x: batch_xs, y_: batch_ys, keep_prob: 1.0})
    predict = sess.run(y_conv, feed_dict={x: yesterday_data, keep_prob: 1.0})
    if np.max(predict) > VALIDPROB:
        print(predict)
        print(yesterday_y)
    else:
        print('less than %g' % VALIDPROB)
    sess.close()
    return predict

def testStockAccuracy(stock):
    #mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
    #stock=StockData('000006')
    #stockD, stockL = stock._read32()
    x = tf.placeholder("float", [None, 256])
    W = tf.Variable(tf.zeros([256, 5]))
    b = tf.Variable(tf.zeros([5]))
    y = tf.nn.softmax(tf.matmul(x, W) + b)
    y_ = tf.placeholder("float", [None, 5])
    #conv1 layer
    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])
    x_image = tf.reshape(x, [-1, 16, 16, 1])
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)   #output 16*16*32
    h_pool1 = max_pool_2x2(h_conv1)                            #output 8*8*32

    #conv2 layer
    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([4 * 4 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 4 * 4 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    keep_prob = tf.placeholder("float")
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
    W_fc2 = weight_variable([1024, 5])
    b_fc2 = bias_variable([5])
    y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
    cross_entropy = -tf.reduce_sum(y_ * tf.log(y_conv))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())
    for i in range(2000):
        batch_xs, batch_ys = stock.net_batch(which='train', num=100)
        if i % 100 == 0:
            train_accuracy = accuracy.eval(feed_dict={
                x: stock.testData, y_: stock.testLabel, keep_prob: 1.0})
            predict = sess.run(y_conv, feed_dict={x: stock.testData, keep_prob: 1.0})
            for n in range(predict.__len__()):
                if np.max(predict[n]) > VALIDPROB:
                    print(predict[n])
                    print(stock.testLabel[n])
            print("step %d, training accuracy %g" % (i, train_accuracy))
        train_step.run(feed_dict={x: batch_xs, y_: batch_ys, keep_prob: 0.8})


if __name__ == "__main__":
    print("main start!")
    stock =StockData('000006')
    stock._read32()
    testStockAccuracy(stock)

    #stockNumS = stockbasics.get_all_stock_code()
    # for stockNum in stockNumS:
    #     try:
    #         stock = StockData(stockNum)
    #         stock._read32()
    #         print(stockNum)
    #         pre_stock(stock)
    #     except:
    #         print(stockNum + " is not valid")




