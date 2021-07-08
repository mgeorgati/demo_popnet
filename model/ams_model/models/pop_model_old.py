from base.base_model import BaseModel
import tensorflow as tf

class PopModel(BaseModel):
    def __init__(self, config):
        super(PopModel, self).__init__(config)
        # call the build_model and init_saver functions.
        self.build_model()
        self.init_saver()

    def build_model(self):
        # Network placeholders 
        # # tf.placeholder
        self.is_training = tf.compat.v1.placeholder(tf.bool)

        self.x = tf.compat.v1.placeholder(tf.float32, shape=[self.config.batch_size, self.config.chunk_height, self.config.chunk_width, sum(self.config.feature_list) + 1], name='x')
        self.x_pop_chunk = tf.compat.v1.placeholder(tf.float32, shape=self.config.batch_size, name='x_pop_chunk')  # sum of population in chunks
        self.x_cur_pop = tf.compat.v1.placeholder(tf.float32, name='x_cur_pop')  # sum of all population in current year
        self.x_proj = tf.compat.v1.placeholder(tf.float32, name='x_proj')  # projection of population in year to come
        self.y_true = tf.compat.v1.placeholder(tf.float32, shape=[self.config.batch_size, self.config.chunk_height, self.config.chunk_width, 1], name='y_true')

        # Padding works like:
        # [[batch size], [chunk height], [chunk width], [no. features]]
        paddings_3 = tf.constant([[0, 0], [1, 1], [1, 1], [0, 0]])  # (3 - 1) / 2 = 1
        paddings_5 = tf.constant([[0, 0], [2, 2], [2, 2], [0, 0]])  # (5 - 1) / 2 = 2
        paddings_7 = tf.constant([[0, 0], [3, 3], [3, 3], [0, 0]])  # (7 - 1) / 2 = 3

        # Network architecture 
        conv1 = tf.layers.conv2d(
            inputs=tf.pad(self.x, paddings_3, "SYMMETRIC"),
            filters=256,
            strides=(1, 1),
            kernel_size=[3, 3], # [filter height, filter width]
            padding="valid",
            activation=tf.nn.relu,
            name='convolution_1')
        """g
        conv1 = tf.layers.conv2d(
            inputs=tf.pad(self.x, paddings_3, "SYMMETRIC"),
            filters=256,
            strides=(1, 1),
            kernel_size=[3, 3], # [filter height, filter width]
            padding="valid",
            activation=tf.nn.relu,
            name='convolution_1')
        """
        # norm1 = tf.nn.local_response_normalization(
        #     conv1,
        #     depth_radius=5,
        #     bias=1,
        #     alpha=1,
        #     beta=0.5,
        #     name='normalization_1')
        #
        # # pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
        #
        conv2 = tf.layers.conv2d(
            inputs=tf.pad(conv1, paddings_3, "SYMMETRIC"),
            filters=256,
            strides=(1, 1),
            kernel_size=[3, 3],
            padding="valid",
            activation=tf.nn.relu,
            name='convolution_2')
        #
        # norm2 = tf.nn.local_response_normalization(
        #     conv2,
        #     depth_radius=5,
        #     bias=1,
        #     alpha=1,
        #     beta=0.5,
        #     name='normalization_2')
        #
        conv3 = tf.layers.conv2d(
            inputs=tf.pad(conv2, paddings_3, "SYMMETRIC"),
            filters=256,
            kernel_size=[3, 3],
            padding="valid",
            activation=tf.nn.relu,
            name='convolution_3')

        # norm3 = tf.nn.local_response_normalization(
        #     conv3,
        #     depth_radius=5,
        #     bias=1,
        #     alpha=1,
        #     beta=0.5,
        #     name='normalization_3')
        #
        # conv4 = tf.layers.conv2d(
        #     inputs=tf.pad(conv3, paddings_3, "SYMMETRIC"),
        #     filters=256,
        #     kernel_size=[3, 3],
        #     strides=(1, 1),
        #     padding="valid",
        #     activation=tf.nn.relu,
        #     name='convolution_4')

        # norm4 = tf.nn.local_response_normalization(
        #     conv4,
        #     depth_radius=5,
        #     bias=1,
        #     alpha=1,
        #     beta=0.5,
        #     name='normalization_4')

        dense1 = tf.layers.dense(inputs=conv3, units=512, activation=tf.nn.relu, name='dense_1')

        self.y = tf.layers.dense(inputs=dense1, units=1, name='y')

        self.y_chunk = tf.subtract(tf.reduce_sum(tf.abs(self.y), axis=0), tf.multiply(self.x_proj, tf.divide(self.x_pop_chunk, self.x_cur_pop)))

        # y_sum = tf.Variable(0)
        #
        # y_sum = tf.add(y_sum, tf.cast(tf.reduce_sum(self.y), tf.int32))
        #
        # y_sum = tf.Variable(y_sum,)

        # self.y_sum = tf.Print(self.y_sum, [self.y_sum], message="This is y_sum: ")
        #
        # b = tf.add(self.y_sum, self.y_sum)

        with tf.name_scope("pop_tot_loss"):
            #self.pop_total_err = tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y)))
            #self.pop_total_err = tf.div(tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y))), tf.cast(tf.size(self.y), tf.float32)) # 573440)
            #label_pop = tf.divide(self.y_pop, self.x_proj)
            #pred_pop = tf.divide(tf.reduce_sum(self.y, axis=0), self.x_proj)
            #self.pop_total_err = tf.reduce_mean(tf.abs(tf.subtract(self.y_pop, tf.reduce_sum(self.y, axis=0))))
            #chunk_pred = tf.reduce_sum(self.y, axis=0)
            chunk_height = tf.cast(self.config.chunk_height, dtype='float32')
            chunk_width = tf.cast(self.config.chunk_width, dtype='float32')
            #chunk_y = tf.divide(tf.multiply(self.x_proj, tf.divide(self.x_pop_chunk, self.x_cur_pop)), tf.multiply(chunk_height, chunk_width))
            self.pop_total_err = tf.abs(tf.divide(self.y_chunk, tf.multiply(chunk_height, chunk_width)))
        with tf.name_scope("pop_cell_loss"):
            # self.root_mean_square_err = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(self.y_true, self.y))))
            self.mean_absolute_err = tf.reduce_mean(tf.abs(tf.subtract(self.y_true, self.y)))
        with tf.name_scope("loss"):
            # Cost function
            # pop_total_err = tf.div(tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y))), tf.size(self.y))

            # MANGLER AT DIVIDE POP_TOTAL_ERR med antallet af celler
            # TensorFlow function for root mean square error

            self.loss_func = tf.add(tf.multiply(self.config.cost_cell, self.mean_absolute_err), tf.multiply(self.config.cost_chunk, self.pop_total_err))
            print(self.loss_func)
            # Initializing the optimizer, that will optimize the root mean square error through backpropagation, and thus learn

            self.train_step = tf.train.AdamOptimizer(self.config.learning_rate).minimize(self.loss_func,
                                                                                    global_step=self.global_step_tensor)
            #self.train_step = tf.train.MomentumOptimizer(self.config.learning_rate).minimize(self.loss_func,
            #                                                                        global_step=self.global_step_tensor)
            #self.train_step = tf.train.GradientDescentOptimizer(self.config.learning_rate).minimize(self.loss_func,
            #                                                                       global_step=self.global_step_tensor)


        with tf.name_scope("y_sum"):
            # tf.Print(self.y_sum, [self.y_sum])
            # a = tf.add(self.y_sum, self.y_sum)

            self.y_sum += tf.reduce_sum(self.y)

    def init_saver(self):
        #here you initalize the tensorflow saver that will be used in saving the checkpoints.
        self.saver = tf.compat.v1.train.Saver(max_to_keep=self.config.max_to_keep)