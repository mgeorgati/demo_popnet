import tensorflow as tf

hello = tf.constant('hello tensorflow')

with tf.compat.v1.Session() as sess:
    print(sess.run(hello))