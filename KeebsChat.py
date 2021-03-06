# Author: Christopher Rossi
# Project Name: KeebsChat - Mechanical Keyboard Chatbot
# Start Date: 5/31/2021
# End Date: 8/28/2021

# Flask Dependencies
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='.')  # '.' means the current directory

# Tensorflow dependencies
import numpy
import numpy as np
import tflearn
import tensorflow as tf
import random

# NLP dependencies
import json
import pickle
import nltk
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()

# Import other files
from apex_webscrape import find_product

product_tags = ['lubes', 'switches', 'keysets', 'deskmats', 'tuning-parts', 'keyboard-kits', 'snacks']

tf.compat.v1.disable_resource_variables

# import our chat-bot intents file
with open("intents.json") as file:
    data = json.load(file)
    # print(data)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output, docs_x, docs_y, ignore_words = pickle.load(f)

except:
    words = []
    labels = []
    docs_x = []
    docs_y = []
    ignore_words = ['?']

    # loop through each sentence in our intents patterns
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            # tokenize each word in the sentence
            w = nltk.word_tokenize(pattern)
            # add to our word list (we do not append since it is already a list)
            words.extend(w)
            # add to document lists
            docs_x.append(w)
            docs_y.append(intent["tag"])
            # add to our labels list
            if intent["tag"] not in labels:
                labels.append((intent["tag"]))

    # steam and lower each word and remove duplicates
    words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))
    # sort label list
    labels = sorted(labels)

    training = []
    output = []
    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w) for w in doc]

        # if word exists, add a 1 otherwise add 0 to the bag
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        # look through label list, see where the tag is and set that value to 1 in the output row
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    # convert to numpy array for tensorflow
    training = np.array(training)
    output = np.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output, docs_x, docs_y, ignore_words), f)

# resets underlying data graph

tf.compat.v1.get_default_graph()

# Input data for model
net = tflearn.input_data(shape=[None, len(training[0])])
# two hidden layers with 8 neurons each
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
# output layer
# softmax --> outputs a probability of each neuron
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)
# DNN --> Deep Neural Network
model = tflearn.DNN(net)
# model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
# model.save("model.tflearn")

# if model exists load it, otherwise retrain and save a new one
try:
    model.load("model.tflearn")
except:
    # fit & save our model
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    # list of tokenized words
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for x in s_words:
        for i, w in enumerate(words):
            if w == x:
                bag[i] = 1

    return numpy.array(bag)


def chat(text):
    while True:
        inp = text
        if inp.lower() == "quit":
            break

        results = model.predict([bag_of_words(inp, words)])
        # returns the greatest value in our list
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        if tag in product_tags:
            return find_product(tag)
        else:
            for tg in data["intents"]:
                if tg["tag"] == tag:
                    responses = tg['responses']

            return random.choice(responses)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chat(userText)


if __name__ == "__main__":
    app.run()
