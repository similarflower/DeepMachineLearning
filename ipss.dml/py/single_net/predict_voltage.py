'''
    Copyright (C) 2005-17 www.interpss.org
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

'''
 Use NN-model to predict the bus voltage for a random selected scale-factor
'''

from datetime import datetime

import tensorflow as tf

import sys
sys.path.insert(0, '..')

import lib.common_func as cf

train_points = 50

# 
# load the IEEE-14Bus case
#
filename = 'testdata/ieee14.ieee'
noBus, noBranch = cf.ipss_app.loadCase(filename, 'BusVoltLoadChangeTrainCaseBuilder')
print(filename, ' loaded,  no of Buses, Branches:', noBus, ', ', noBranch)

# define model size
size = noBus * 2
#print('size: ', size)

# define model variables
W = tf.Variable(tf.zeros([size,size]))
b = tf.Variable(tf.zeros([size]))

init = tf.initialize_all_variables()

# define model

def nn_model(data):
    output = tf.matmul(data, W) + b
    return output

# define loss 
x = tf.placeholder(tf.float32, [None, size])
y = tf.placeholder(tf.float32)

error = tf.square(nn_model(x) - y)
loss = tf.reduce_sum(error)

# define training optimization
optimizer = tf.train.GradientDescentOptimizer(cf.learning_rate)
train = optimizer.minimize(loss)

# run the computation graph
with tf.Session() as sess :
    sess.run(init)
    
    # run the training part
    # =====================
 
    print('Begin training: ', datetime.now())
     
    # retrieve training set
    trainSet = cf.ipss_app.getTrainSet(train_points)
    train_x, train_y = cf.transfer2PyArrays(trainSet)
    
    #print2DArray(train_x, 'train_xSet', 'train_x')
    #print2DArray(train_y, 'train_ySet', 'train_y')
    
    # run the training part
    for i in range(cf.train_steps):
        if (i % 1000 == 0) : print('Training step: ', i) 
        sess.run(train, {x:train_x, y:train_y})

    print('End training: ', datetime.now())
    '''
    print('W1: ', sess.run(W1))
    print('b1: ', sess.run(b1))
    '''
 
    # run the verification part
    # =========================
    
    # retrieve a test case
    testCase = cf.ipss_app.getTestCase();
    test_x, test_y = cf.transfer2PyArrays(testCase)
    #printArray(test_x, 'test_x')
    #printArray(test_y, 'test_y')
    
    # compute model output (network voltage)
    model_y = sess.run(nn_model(x), {x:test_x})
    #printArray(model_y[0], 'model_y')
    
    netVoltage = cf.transfer2JavaDblAry(model_y[0], size)
    print('model out mismatch: ', cf.ipss_app.getMismatchInfo(netVoltage))
