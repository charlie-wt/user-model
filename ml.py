import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import tensorflow as tf
import numpy as np
import math
import statistics as st

import traverser as tr
import page as pg
import user as us
import reading as rd
import heuristics as hs
import ranker as rk
import ls
import printer as pt

##### ml #####################
# machine learning stuff.
##############################

def formalise ( story, ppr, cache=None, prnt=False, exclude_poi=False ):
# put list of pages (forming a path) into a form that can be interpreted by ml.
    if prnt: print('formalised path data:')
    xs = []
    ys = []

    # create stuff
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    if cache is None: cache = ls.auto_dict()

    # perform reading
    count = 1
    for r in ppr:
        path = ppr[r]
        visible = pg.update_all(story.pages, story, reading, user)
        for i in range(0, len(path)-1):
            # calculate heuristics (and rankings) for each option, and store
            if len(visible) > 1:
                # add heuristic/ranking information to input vector
                xs += make_input(story, user, visible, cache, exclude_poi)
                for p in visible:
                    # add result (whether the page was chosen) to output vector
                    ys.append((1 if p == path[i] else 0))

                    if prnt: print(count, ':', ys[-1], '<-', xs[-1])
                    count += 1

            # move to next page
            move_to_idx = ls.index(visible, path[i].id)
            visible = user.move(move_to_idx, visible, story, reading)
        tr.reset(story, reading, user)

    if len(ys) == 0:
        raise ValueError('Story supplied to formalise contains no choices.')

    return (xs, ys)

def make_input ( story, user, pages, cache=None, exclude_poi=False ):
# get a tuple of heuristics + rankings for each page.
    if type(pages) != list: pages = [pages]

    xs = []

    # get rankings
    walk_dist_ranking = rk.walk_dist(user, story, pages, cache)
    visits_ranking = rk.visits(user, story, pages, cache)
    alt_ranking = rk.alt(user, story, pages, cache)
    if not exclude_poi:
        poi_ranking = rk.poi(user, story, pages, cache)
    mention_ranking = rk.mentioned(user, story, pages, cache)

    for p in pages:
        # get heuristic values for this page
        walk_dist = hs.walk_dist(p, user, story, cache)
        visits = hs.visits(p, user)
        alt = hs.altitude(p, user, story, cache)
        if not exclude_poi:
            poi = hs.points_of_interest(p, user, story, cache)
        mention = hs.mentioned(p, user, story, cache)

        # get ranking for this page
        r_dst = walk_dist_ranking[p]
        r_vis = visits_ranking[p]
        r_alt = alt_ranking[p]
        if not exclude_poi:
            r_poi = poi_ranking[p]
        r_men = mention_ranking[p]

        # add heuristics/values to input vector
        if not exclude_poi:
#            xs.append((walk_dist, visits, alt, poi, mention,
#                       r_dst, r_vis, r_alt, r_poi, r_men))
             xs.append((r_dst, r_vis, r_alt, r_poi, r_men))
        else:
#            xs.append((walk_dist, visits, alt, mention,
#                       r_dst, r_vis, r_alt, r_men))
             xs.append((r_dst, r_vis, r_alt, r_men))

    return xs

def logreg ( story, ppr, cache=None, learning_rate=0.01, epochs=25,
                   batch_size=None, num_folds = 1, train_prop=0.9, prnt=False, exclude_poi=False ):
    # get data in correct format
    data = formalise(story, ppr, cache, exclude_poi=exclude_poi)
    models = []

    # get info about data
    if batch_size is None: batch_size=len(data[0])
    num_features = len(data[0][0])  # the heuristics and rankings describing a page.
    num_classes = max(data[1])+1    # to choose, or not to choose a page.
    num_samples = len(data[0])      # number of movements between pages.

    # Xs & Ys: total inputs and true labels, for all samples.
    Xs = data[0]
    Ys = one_hot(data[1], num_classes)

    # size of training/testing set; do for cross validation if num_folds > 1.
    if num_folds > 1:
        num_testing = int(num_samples / num_folds)
        num_training = num_samples - num_testing
    else:
        num_training = int(train_prop * num_samples)
        num_testing = num_samples - num_training

    # define tensorflow graph
    x  = tf.placeholder(tf.float32, [None, num_features])
    y_ = tf.placeholder(tf.float32, [None, num_classes])

    # model weights
    w = tf.Variable(tf.zeros([num_features, num_classes]))
    b = tf.Variable(tf.zeros([num_classes]))

    # construct model
    # model calculates y, to test against y_ for cost. Is essentially y=mx+c.
    model = tf.matmul(x, w) + b
    # our cost function, to see how far from the truth we are:
    cost = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=model)
    # our gradient descent optimizer (to minimize cost via. changing w & b):
    gd = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    init = tf.global_variables_initializer()
    for i in range(num_folds):
        # split data into training & testing
        # Xtr & Ytr: training set
        Xtr = Xs[:i*num_testing] + Xs[(i+1)*num_testing:]
        Ytr = Ys[:i*num_testing] + Ys[(i+1)*num_testing:]
        # Xts & Yts: testing set
        Xts = Xs[i*num_testing:(i+1)*num_testing]
        Yts = Ys[i*num_testing:(i+1)*num_testing]

        with tf.Session() as sess:
            sess.run(init)

            # training cycle
            num_batches = math.ceil(num_training / batch_size)
            bxs = batches(Xtr, batch_size)
            bys = batches(Ytr, batch_size)
            for epoch in range(epochs):
                av_cost = 0

                for j in range(num_batches):
                    _, c = sess.run(
                        [gd, cost],
                        feed_dict = { x: bxs[j], y_: bys[j] }
                    )
                    av_cost = c / num_batches

                if prnt and num_folds <= 1:
                    print('epoch', (epoch+1), 'cost =', av_cost)

            correct_prediction = tf.equal(tf.argmax(model, 1), tf.argmax(y_, 1))
            acc = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            if prnt:
                print('results', end='')
                print((' for model '+str(i+1)+':') if num_folds > 1 else ':')
                print('w =', sess.run(w))
                print('b =', sess.run(b))
                if train_prop < 1:
                    print('accuracy:', pt.pc(acc.eval({ x: Xts, y_: Yts }), dec=2))

            models.append({
                'w': sess.run(w),
                'b': sess.run(b),
                'acc': acc.eval({ x: Xts, y_: Yts })
            })

    av_w = [ [0, 0] for i in range(num_features) ]
    av_b = [0, 0]
    for i in range(len(models)):
        for j in range(num_features):
            av_w[j][0] += models[i]['w'][j][0]
            av_w[j][1] += models[i]['w'][j][1]
        av_b[0] += models[i]['b'][0]
        av_b[1] += models[i]['b'][1]
    for i in range(num_features):
        av_w[i][0] /= len(models)
        av_w[i][1] /= len(models)
    av_b[0] /= len(models)
    av_b[1] /= len(models)

    average = {
        'w': av_w,
        'b': av_b,
    }
    if prnt and num_folds > 1:
        print('average model:')
        print('w =', average['w'])
        print('b =', average['b'])
    return average

def one_hot ( data, num_classes=None ):
# convert a list of class labels (0, 1, 2 etc.) into a list of probability
# distributions where all probabilities are 0, except the true value which is 1.
    oh = []
    if num_classes is None: num_classes = max(data) + 1

    for i in range(len(data)):
        prob_dist = [0] * num_classes
        prob_dist[data[i]] = 1
        oh.append(prob_dist)

    return oh

def batches ( data, batch_size ):
# turn big list of data into a bunch of batches
    bs = batch_size
    nb = math.ceil(len(data)/batch_size)
    return [ data[i*bs:(i+1)*bs] for i in range(nb) ]

def nn ( story, path, cache=None, prnt=False ):
    raise NotImplementedError('lol')
