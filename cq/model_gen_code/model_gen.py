import numpy as np
import csv
import tensorflow as tf
import numpy as np
import os
from sklearn import metrics



def linear(input_, output_size, scope=None, stddev=0.02, bias_start=0.0, with_w=False):
    shape = input_.get_shape().as_list()

    with tf.variable_scope(scope or "Linear"):
        matrix = tf.get_variable("Matrix", [shape[1], output_size], tf.float32,
                                 tf.random_normal_initializer(stddev=stddev))
        bias = tf.get_variable("bias", [output_size],
            initializer=tf.constant_initializer(bias_start))
        if with_w:
            return tf.matmul(input_, matrix) + bias, matrix, bias
        else:
            return tf.matmul(input_, matrix) + bias

def lrelu(x, alpha):
    return tf.nn.relu(x) - alpha * tf.nn.relu(-x)



class Layer:

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.activation_function = kwargs['activation_function']  # none, relu, leakyrelu, elu, sigmoid
        self.node_num = kwargs['node_num']
        self.dropout = kwargs['dropout'] # True, False

        if self.dropout:
            self.dropout_prob = kwargs['dropout_prob']


class ModelGen:

    def __init__(self, **kwargs):
        self.batch_size = kwargs['batch_size']
        self.train_num = kwargs['train_num']
        self.val_num = kwargs['val_num']
        self.test_num = kwargs['test_num']
        self.input_list = kwargs['input_list'] # ex) ['X1', 'X6', 'X11']
        self.output_list = kwargs['output_list']
        self.data_filename = kwargs['data_filename']
        self.epoch = kwargs['epoch']
        self.layer_list = kwargs['layer_list'] # starts from input to output. @ses class Layer
        self.optimizer = kwargs['optimizer'] # adam, rmsprop, sgd
        self.learning_rate = kwargs['learning_rate']

        if self.optimizer == 'adam':
            self.beta1 = kwargs['beta1']
            self.beta2 = kwargs['beta2']


        self.layer_idx = 1 # used for generating unique layer identifiers


    def output_score(self, sess, t_x, y_dim):
        test_num = t_x.shape[0]
        test_score = np.zeros([test_num, y_dim])

        idx = 0
        test_idx = 0
        while idx <= test_num - self.batch_size:
            batch_x = t_x[idx:idx + self.batch_size]

            test_score[test_idx:test_idx + self.batch_size] = sess.run(self.model_output, {self.x:batch_x})
            idx += self.batch_size
            test_idx += self.batch_size

        batch_x = t_x[-self.batch_size:]

        temp_output = sess.run(self.model_output, {self.x:batch_x})
        test_score[test_idx:] = temp_output[(self.batch_size - (test_num - idx)):]

        return test_score


    def measure_error(self, sess, t_x, t_y):
        predict_y = self.output_score(sess, t_x, t_y.shape[1])

        rmse = np.sqrt(metrics.mean_squared_error(t_y[:, 0], predict_y[:, 0]))
        mae = metrics.mean_absolute_error(t_y[:, 0], predict_y[:, 0])

        return rmse, mae


    def run(self):
        self.layer_idx = 1

        # read body
        with open(self.data_filename, "rb") as f:
            data = np.loadtxt(f, delimiter=",", skiprows=1)

        # read header
        with open(self.data_filename, "r") as f:
            reader = csv.reader(f)
            header = next(reader)

        input_indices = [header.index(name) for name in self.input_list]
        output_indices = [header.index(name) for name in self.output_list]

        X = data[:, input_indices]
        Y = data[:, output_indices]


        # load data
        feature_dim = X.shape[1]
        y_dim = Y.shape[1]


        # shuffle
        np.random.seed(112)
        rarr = np.arange(X.shape[0])
        np.random.shuffle(rarr)

        X = X[rarr]
        Y = Y[rarr]


        # split data into train and test
        train_num = self.train_num
        test_num = self.test_num
        val_num = self.val_num

        train_x = X[:train_num]
        val_x = X[train_num:train_num + val_num]
        test_x = X[train_num + val_num:train_num + val_num + test_num]
        train_y = Y[:train_num]
        val_y = Y[train_num:train_num + val_num]
        test_y = Y[train_num + val_num:train_num + val_num + test_num]


        # build model
        self.x = tf.placeholder(tf.float32, [self.batch_size, feature_dim], name='x')
        self.y = tf.placeholder(tf.float32, [self.batch_size, y_dim], name='y')

        h = self.x
        for layer in self.layer_list:
            h = self.add_layer(h, layer)
        self.model_output = linear(h, y_dim, 'out')

        self.loss = tf.reduce_mean(tf.square(self.model_output - self.y))

        if self.optimizer == 'adam':
            self.train_op = tf.train.AdamOptimizer(self.learning_rate, beta1=self.beta1, beta2=self.beta2).minimize(self.loss)
        elif self.optimizer == 'rmsprop':
            self.train_op = tf.train.RMSPropOptimizer(self.learning_rate).minimize(self.loss)
        elif self.optimizer == 'sgd':
            self.train_op = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self.loss)
        else:
            # error
            print('Error: invalid optimizer = %s' % self.optimizer)


        # ====================================================================================================
        # train
        # ====================================================================================================

        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            cur_step = 0

            for epoch in range(self.epoch):

                n_batch = int(train_num/self.batch_size)
                for i in range(n_batch):
                    i = np.random.randint(0, train_num - self.batch_size)

                    batch_feature = train_x[i:i+self.batch_size]
                    batch_y = train_y[i:i+self.batch_size]

                    _, o = sess.run([self.train_op, self.model_output], {self.x:batch_feature, self.y:batch_y})
                    cur_step += 1

                # train & test rmse error
                test_rmse, test_mae = self.measure_error(sess, test_x, test_y)
                train_rmse, train_mae = self.measure_error(sess, train_x, train_y)
                print('%d,%.4f,%.4f' % (epoch, train_rmse, test_rmse))

    def add_layer(self, input_, layer):
        h = linear(input_, layer.node_num, 'lin%d' % self.layer_idx)
        self.layer_idx += 1

        if layer.activation_function == 'relu':
            h = tf.nn.relu(h)
        elif layer.activation_function == 'leakyrelu':
            h = lrelu(h, 0.2)
        elif layer.activation_function == 'elu':
            h = tf.nn.elu(h)
        elif layer.activation_function == 'sigmoid':
            h = tf.nn.sigmoid(h)

        if layer.dropout:
            h = tf.nn.dropout(h, 1 - layer.dropout_prob)

        return h
