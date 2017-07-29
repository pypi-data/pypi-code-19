import tensorflow as tf 
from   tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets("MNIST_DATA/",one_hot=True)
sess  = tf.InteractiveSession()
x = tf.placeholder(tf.float32,[None,784])
W = tf.Variable(tf.zeros([784,10]))
b = tf.Variable(tf.zeros([10]))

y = tf.nn.softmax(tf.matmul(x,W) + b)
y_ = tf.placeholder(tf.float32,[None,10])

cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_*tf.log(y),reduction_indices=[1]))

train = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

"""init the globals"""
tf.global_variables_initializer().run()
"""init the accuracy prediction"""

correct_prediction = tf.equal(tf.argmax(y,1),tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))

for i in range(1000):
	batch_xs,batch_ys = mnist.train.next_batch(100)
	train.run({x:batch_xs,y_:batch_ys})
	if i % 20 == 0:
		print(accuracy.eval({x:mnist.test.images,y_:mnist.test.labels}))

