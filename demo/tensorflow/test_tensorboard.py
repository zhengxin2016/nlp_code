#!/usr/bin/env python3
import os, sys
import tensorflow as tf
import numpy as np

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' #all info
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' #warning, error
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #error

def add_layer(inputs, in_size, out_size, activation_function=None):
    with tf.name_scope('weights'):
        Weights = tf.Variable(tf.random_normal([in_size, out_size]))
        tf.summary.histogram('weights', Weights)
    with tf.name_scope('biases'):
        biases = tf.Variable(tf.zeros([1, out_size]) + 0.1)
        tf.summary.histogram('biases', biases)
    with tf.name_scope('Wx_plus_b'):
        Wx_plus_b = tf.matmul(inputs, Weights) + biases
        keep_prob = 1
        Wx_plus_b = tf.nn.dropout(Wx_plus_b, keep_prob)
        tf.summary.histogram('Wx_plus_b', Wx_plus_b)
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b)
    tf.summary.histogram('outputs', outputs)
    return outputs

x_data = np.linspace(-1, 1, 300)[:, np.newaxis]
noise = np.random.normal(0, 0.05, x_data.shape)
y_data = np.square(x_data) - 0.5 + noise

with tf.name_scope('input_x'):
    xs = tf.placeholder(tf.float32, [None, 1])
with tf.name_scope('input_y'):
    ys = tf.placeholder(tf.float32, [None, 1])

with tf.name_scope('L1'):
    l1 = add_layer(xs, 1, 10, activation_function=tf.nn.relu)
with tf.name_scope('outputs'):
    prediction = add_layer(l1, 10, 1, activation_function=None)

with tf.name_scope('loss'):
    loss = tf.reduce_mean(tf.reduce_sum(tf.square(ys-prediction),
        reduction_indices=[1]))
    tf.summary.scalar('loss', loss)

with tf.name_scope('train_step'):
    train_step = tf.train.GradientDescentOptimizer(0.1).minimize(loss)

init = tf.global_variables_initializer()
saver = tf.train.Saver()
sess = tf.Session()
merged = tf.summary.merge_all()
writer = tf.summary.FileWriter('logs/', sess.graph)
sess.run(init)
for i in range(1000):
    sess.run(train_step, feed_dict={xs:x_data, ys:y_data})
    if i % 100 == 0:
        print(sess.run(loss, feed_dict={xs:x_data, ys:y_data}))
        result = sess.run(merged, feed_dict={xs:x_data, ys:y_data})
        writer.add_summary(result, i)
        save_path = saver.save(sess, "save/save.ckpt")
        print("Save to path:", save_path)
sess.close()


##########################
print('\n\nrestore....\n')
saver = tf.train.Saver()
sess = tf.Session()
saver.restore(sess, 'save/save.ckpt')
for i in range(1000):
    sess.run(train_step, feed_dict={xs:x_data, ys:y_data})
    if i % 100 == 0:
        print(sess.run(loss, feed_dict={xs:x_data, ys:y_data}))

while 1:
    x = input('input:')
    x = float(x.strip())
    y = sess.run(prediction, feed_dict={xs:[[x]]})
    print(x, y)





