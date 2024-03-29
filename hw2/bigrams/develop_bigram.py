#!/usr/bin/python3
#author: Fan Luo
import numpy as np
import string
from collections import Counter
import train_bigram         # train-bigram.py

# Sigmoid function
def sigmoid(z):
    if(z < -20):
        return 0
    else:
        return 1 / (1 + np.exp(-z))

def DevelData_preprocess(datafile):
    with open(datafile, 'r') as dev:
        lines = [line.lower() for line in dev]

        num_spam = 0
        Y = []
        word_count_list = []
        biword_count_list = []

        for line in lines:                  # each message
            for c in string.punctuation:    # remove all punctuation
                line = line.replace(c, " ")
            if(line.split()[0] == "spam"):
                Y.append(1)         # labels in develop dataset
                num_spam += 1
            else:
                Y.append(0)

            message_word_count = Counter()
            message_biword_count = Counter()

            for w in range(len(line.split())):
                if(w > 0):
                    word = line.split()[w]
                    message_word_count[word] += 1   # count word's frequency among each message
                    if(w < len(line.split()[1:])):
                        biword = line.split()[w] + ' ' + line.split()[w+1]
                        message_biword_count[biword] += 1
            word_count_list.append(message_word_count)
            biword_count_list.append(message_biword_count)

        return(Y, word_count_list, biword_count_list, num_spam)


def loadmodel(modelfile, word_counts, biword_counts, num_message):

    with open(modelfile, 'r') as model:
        content = [m.rstrip("\n") for m in model]
        features = [(x.split('\t')[0]).strip("'") for x in content[1:]]
        theta = [float(x.split('\t')[1]) for x in content[1:]]

        X = np.zeros((num_message, len(features)))
        for i in range(num_message):
            for j in range(len(features)):
                    X[i][j] = word_counts[i][features[j]]
                    if(X[i][j] == 0):    #feature[j] is not a word or this word not appear in message[i]
                        X[i][j] = biword_counts[i][features[j]]

        return (theta, X)


def tune():

    frequencies = [1, 10, 100, 200, 300]
    rates = [0.01, 0.1, 1, 10, 100]
    epoches = [1, 50, 100, 200, 300]
    sizes = [1, 100, 500, 800, 1000]


    (devel_Y, word_counter_list, biword_counter_list, n_spam) = DevelData_preprocess('SMSSpamCollection.devel')

    with open('develop_result_bigram.txt', 'w') as output:
        output.write("frequency_threshold | learning_rate | epoch_limit | batch_size |\tAccuracy | Precision | Recall\n")

        #different combination of params
        for f in frequencies:
            for r in rates:
                for e in epoches:
                    for s in sizes:
                        train_bigram.train(f, r, e, s)
                        (theta, devel_X) = loadmodel('model_bigram.txt', word_counter_list, biword_counter_list, len(devel_Y))

                        decision = np.zeros(len(devel_Y))
                        match = 0
                        tp = 0
                        positives = 0

                        for i in range(len(devel_Y)):
                            h = sigmoid(np.dot(devel_X[i], theta))
                            if(h > 0.5):
                                decision[i] = 1
                                positives += 1
                                if(decision[i] == devel_Y[i]):
                                    match += 1
                                    tp += 1
                            else:
                                decision[i] = 0
                                if(decision[i] == devel_Y[i]):
                                    match += 1

                        accuracy = match / len(devel_Y)
                        precision = tp / positives
                        recall = tp / n_spam
                        output.write("%s\t %s\t %s\t %s\t %.2f%%\t %.2f%%\t  %.2f%%\n" % (str(f), str(r), str(e), str(s), 100*accuracy, 100*precision, 100*recall))


if __name__ == '__main__':
    tune()