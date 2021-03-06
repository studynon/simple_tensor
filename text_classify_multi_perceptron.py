# reference link
# https://github.com/dmesquita/understanding_tensorflow_nn

import pandas as pd
import numpy as np
import tensorflow as tf
from collections import Counter
from sklearn.datasets import fetch_20newsgroups

# %% small example How TensorFlow works
# import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import tensorflow as tf
my_graph = tf.Graph()
with tf.Session(graph=my_graph) as sess:
    x = tf.constant([1,3,6])
    y = tf.constant([1,1,1])
    op = tf.add(x,y)
    result = sess.run(fetches=op)
    print(result)

# %% how to manipulate data
vocab = Counter()

text = "Hi from Brazil"
# Get all words
for word in text.split(' '):
    word_lowercase = word.lower()
    vocab[word_lowercase]+=1
# Convert words to indexes
def get_word_2_index(vocab):
    word2index = {}
    for i,word in enumerate(vocab):
        word2index[word] = i
    return word2index
# Now we have an index
word2index = get_word_2_index(vocab)

total_words = len(vocab)
# This is how we create a numpy array (our matrix)
matrix = np.zeros((total_words), dtype=float)

# Now we fill the values
for word in text.split():
    matrix[word2index[word.lower()]] += 1

print("Hi from Brazil:", matrix)

matrix = np.zeros((total_words),dtype=float)
text = "Hi"
for word in text.split():
    matrix[word2index[word.lower()]] += 1

print("Hi:", matrix)

# load data
from sklearn.datasets import fetch_20newsgroups
categories = ['comp.graphics', 'sci.space', 'rec.sport.baseball']
newsgroups_train = fetch_20newsgroups(subset='train', categories=categories)
newsgroups_test = fetch_20newsgroups(subset='test', categories=categories)

print('total texts in train:',len(newsgroups_train.data))
print('total texts in test:',len(newsgroups_test.data))

# Get datasets' vocab
vocab = Counter()
for text in newsgroups_train.data:
    for word in text.split(' '):
        vocab[word.lower()]+=1
for text in newsgroups_test.data:
    for word in text.split(' '):
        vocab[word.lower()]+=1
print("Total words:",len(vocab))

total_words = len(vocab)

def get_word_2_index(vocab):
    word2index = {}
    for i,word in enumerate(vocab):
        word2index[word.lower()] = i

    return word2index

word2index = get_word_2_index(vocab)

print("Index of the word 'the':",word2index['the'])

def get_batch(df,i,batch_size):
    batches = []
    results = []
    texts = df.data[i*batch_size:i*batch_size+batch_size]
    categories = df.target[i*batch_size:i*batch_size+batch_size]
    for text in texts:
        layer = np.zeros(total_words,dtype=float)
        for word in text.split(' '):
            layer[word2index[word.lower()]] += 1

        batches.append(layer)

    for category in categories:
        y = np.zeros((3),dtype=float)
        if category == 0:
            y[0] = 1.
        elif category == 1:
            y[1] = 1.
        else:
            y[2] = 1.
        results.append(y)


    return np.array(batches),np.array(results)


# %%
# Parameters
learning_rate = 0.01#0.001
training_epochs = 10
batch_size = 150
display_step = 1

# Network Parameters
n_hidden_1 = 100      # 1st layer number of features
n_hidden_2 = 100       # 2nd layer number of features
n_input = total_words # Words in vocab
n_classes = 3         # Categories: graphics, sci.space and baseball

input_tensor = tf.placeholder(tf.float32, [None, n_input], name='input')
output_tensor = tf.placeholder(tf.float32, [None, n_classes], name='output')

# %% build graph
# n_hidden_1 = 10
# n_hidden_2 = 5
# n_input = total_words
# n_classes = 3

def multilayer_perceptron(input_tensor, weights, biases):
    layer_1_multiplication = tf.matmul(input_tensor, weights['h1'])
    layer_1_addition = tf.add(layer_1_multiplication, biases['b1'])
    layer_1_activation = tf.nn.relu(layer_1_addition)

    # Hidden layer with RELU activation
    layer_2_multiplication = tf.matmul(layer_1_activation, weights['h2'])
    layer_2_addition = tf.add(layer_2_multiplication, biases['b2'])
    layer_2_activation = tf.nn.relu(layer_2_addition)

    # Output layer with linear activation
    out_layer_multiplication = tf.matmul(layer_2_activation, weights['out'])
    out_layer_addition = out_layer_multiplication + biases['out']

    return out_layer_addition

# Store layers weight & bias
weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}


# Construct model
prediction = multilayer_perceptron(input_tensor, weights, biases)

# Define loss
entropy_loss = tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=output_tensor)
loss = tf.reduce_mean(entropy_loss)

# syntactic sugar does two things:
# 1. compute_gradients(loss, <list of variables>)
# 2. apply_gradients(<list of variables>)
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss)

# Initializing the variables
init = tf.global_variables_initializer()

# %% Run model
training_epochs = 10
# Lauch the graph
with tf.Session() as sess:
    sess.run(init)
    # Training cycle
    for epoch in range(training_epochs):
        avg_cost = 0.
        total_batch = int(len(newsgroups_train.data)/batch_size)
        # Loop over all batches
        for i in range(total_batch):
            batch_x, batch_y = get_batch(newsgroups_train,i,batch_size)
            # Run optimization op (backprop) and cost op (to get loss value)
            c,_ = sess.run([loss,optimizer], feed_dict={input_tensor:batch_x, output_tensor:batch_y})
            # Compute average loss
            avg_cost += c / total_batch
        # Display logs per epoch step
        if epoch % display_step == 0:
            print("Epoch:", '%04d' % (epoch+1), "loss=", \
                "{:.9f}".format(avg_cost))
    print("Optimization Finished!")
    # Test model
    index_prediction = tf.argmax(prediction, 1)
    index_correct = tf.argmax(output_tensor, 1)
    correct_prediction = tf.equal(index_prediction, index_correct)

    # Calculate accuracy
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))
    total_test_data = len(newsgroups_test.target)
    batch_x_test, batch_y_test = get_batch(newsgroups_test,0,total_test_data)
    print('Accuracy:', accuracy.eval({input_tensor:batch_x_test, output_tensor:batch_y_test}))
