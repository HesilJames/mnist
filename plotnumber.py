import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
batch_xs,batch_ys=mnist.train.next_batch(100)

#print(batch_xs[0])

f, a = plt.subplots(1, 1, figsize=(1, 1))
a.imshow(np.reshape(batch_xs[0], (28, 28)))
plt.show()
print(batch_ys[0])
#plt.plot_date(tf.reshape(batch_xs[0],[28,28]))
