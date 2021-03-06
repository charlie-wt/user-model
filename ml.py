import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import tensorflow as tf
import numpy as np
import math
from collections import OrderedDict

import traverser as tr
import page as pg
import user as us
import reading as rd
import heuristics as hs
import ranker as rk
import cache as ch
import ls
import printer as pt

'''
ml

machine learning stuff.
'''

def formalise ( ppr, cache=None, prnt=False, normalise=False,
                exclude_poi=False, enforce_ordering=True ):
    ''' put list of pages (forming a path) into a form that can be interpreted
    by ml.
    '''
    if len(ppr) == 0:
        raise ValueError('no logged readings to formalise.')

    # possibly order ppr (by reading name), for consistent learned models.
    if enforce_ordering:
        ppr = OrderedDict(sorted(ppr.items(), key = lambda e: e[0].id))

    if prnt: print('formalised path data:')
    xs = []
    ys = []

    # create stuff
#    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    if cache is None: cache = ch.Cache()

    # perform reading
    count = 1
    for r in ppr:
        path = ppr[r]
        story = r.story
        reading = rd.Reading("temp-reading", story)
        # put user in the middle at the start?
        visible = pg.update_all(story.pages, story, reading, user)
        locs = (0, 0)
        have_location = 0
        for p in visible:
            loc = p.get_loc(story)
            if loc:
                locs = (locs[0]+loc[0], locs[1]+loc[1])
                have_location += 1
        if have_location != 0:
            locs = (locs[0]/have_location, locs[1]/have_location)
            user.loc = locs

        visible = pg.update_all(story.pages, story, reading, user)
        for i in range(len(path)):
            # calculate heuristics (and rankings) for each option, and store
            if len(visible) > 1:
                # add heuristic/ranking information to input vector
                xs += make_input(story, user, visible, cache, exclude_poi)
                for p in visible:
                    # add result (whether the page was chosen) to output vector
                    ys.append(1 if p == path[i] else 0)

                    if prnt: print(count, ':', ys[-1], '<-', xs[-1])
                    count += 1

            # move to next page
            move_to_idx = ls.index(visible, path[i].id)
            visible = user.move(move_to_idx, visible, story, reading)
        tr.reset(story, reading, user)
        if prnt: print('---')

    if len(ys) == 0:
        raise ValueError('Stories supplied to formalise contains no choices.')

    if normalise:
        xs = normalise_inputs(xs)

    return (xs, ys)

def make_input ( story, user, pages, cache=None, exclude_poi=False ):
    ''' get a tuple of heuristics + rankings for each page. '''
    if type(pages) != list: pages = [pages]

    xs = []

    # get rankings over all pages
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
            xs.append([walk_dist, visits, alt, poi, mention,
                       r_dst, r_vis, r_alt, r_poi, r_men])
#             xs.append((r_dst, r_vis, r_alt, r_poi, r_men))
        else:
            xs.append([walk_dist, visits, alt, mention,
                       r_dst, r_vis, r_alt, r_men])
#             xs.append((r_dst, r_vis, r_alt, r_men))

    return xs

def normalise_inputs ( inputs,
                       in_means=None,  in_stddevs=None,
                       out_means=None, out_stddevs=None ):
    ''' normalise the inputs. if in_means/stddevs is set, use their values as
    the means and standard deviations of each of the features/columns of the
    inputs. If out_means/stddevs is set, write the means and standard
    deviations of each column to them.
    '''
    num_rows = len(inputs)
    num_cols = len(inputs[0])
    normed = inputs[:]

    for col in range(num_cols):
        old_vals = [ row[col] for row in inputs ]

        mean = np.mean(old_vals, axis=0) if in_means is None else in_means[col]
        stddev = np.std(old_vals, axis=0) if in_stddevs is None else in_stddevs[col]

        if out_means is not None: out_means.append(mean)
        if out_stddevs is not None: out_stddevs.append(stddev)
        if stddev == 0: stddev = 1

        new_vals = [ (v - mean)/stddev for v in old_vals ]
        for row, val in zip(range(num_rows), new_vals):
            normed[row][col] = val
    return normed

def logreg ( ppr, cache=None, learning_rate=0.01, epochs=100,
             batch_size=1, num_folds=1, train_prop=0.9, random_weights=False,
             convergence_threshold = 0.0001, exclude_poi=False, prnt=False ):
    # setup
    data = formalise(ppr, cache, exclude_poi=exclude_poi)
    models = []
    cross_validate = num_folds > 1
    regularisation_lambda = 0.01
    check_convergence = convergence_threshold and convergence_threshold > 0
    # just for the benefit of the rankers
    if not rk.means or not rk.stddevs:
        normalise_inputs(data[0], out_means=rk.means, out_stddevs=rk.stddevs)

    # get info about data
    if batch_size is None: batch_size=len(data[0])
    num_features = len(data[0][0])  # the heuristics and rankings describing a page.
    num_classes = max(data[1])+1    # to choose, or not to choose a page.
    num_samples = len(data[0])      # number of movements between pages.

    # size of training/testing set; do for cross validation if cross_validate.
    if cross_validate:
        num_testing = int(num_samples / num_folds)
        num_training = num_samples - num_testing
    else:
        num_training = int(train_prop * num_samples)
        num_testing = num_samples - num_training

    # Xs & Ys: total inputs and true labels, for all samples.
    Xs = data[0]
    Ys = one_hot(data[1], num_classes)

    # define tensorflow graph
    x  = tf.placeholder(tf.float32, [None, num_features])
    y_ = tf.placeholder(tf.float32, [None, num_classes])

    # model weights
    if random_weights:
        w = tf.Variable(tf.random_normal([num_features, num_classes]))
        b = tf.Variable(tf.random_normal([num_classes]))
    else:
        w = tf.Variable(tf.zeros([num_features, num_classes]))
        b = tf.Variable(tf.zeros([num_classes]))

    # construct model
    # model calculates y, to test against y_ for cost. Is essentially y=mx+c.
    model = tf.matmul(x, w) + b
    # our cost function, to see how far from the truth we are:
    cost = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=model)
    # L2 regularisation
    cost = tf.reduce_mean(tf.reduce_mean(cost) + regularisation_lambda*tf.nn.l2_loss(w))
    # our gradient descent optimizer (to minimize cost via. changing w & b):
    gd = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    for i in range(num_folds):
        # split data into training & testing
        # Xtr & Ytr: training set
        Xtr = Xs[:i*num_testing] + Xs[(i+1)*num_testing:]
        Ytr = Ys[:i*num_testing] + Ys[(i+1)*num_testing:]
        # Xts & Yts: testing set
        Xts = Xs[i*num_testing:(i+1)*num_testing]
        Yts = Ys[i*num_testing:(i+1)*num_testing]

        # normalise input sets. use training set's means/standard deviations
        mn = []
        sd = []
        Xtr = normalise_inputs(Xtr, out_means=mn, out_stddevs=sd)
        Xts = normalise_inputs(Xts, in_means=mn, in_stddevs=sd)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            # training cycle
            num_batches = math.ceil(num_training / batch_size)
            bxs = batches(Xtr, batch_size)
            bys = batches(Ytr, batch_size)
            old_cost = None
            for epoch in range(epochs):
                av_cost = 0

                for j in range(num_batches):
                    # perform gradient descent optimisation on model.
                    _, c = sess.run(
                        [gd, cost],
                        feed_dict = { x: bxs[j], y_: bys[j] }
                    )
                    av_cost += c / num_batches

                if prnt and not cross_validate:
                    print('epoch', (epoch+1), 'cost =', av_cost)
                # check for convergence of the model
                if check_convergence:
                    if old_cost and abs(av_cost - old_cost) < convergence_threshold:
                        if prnt: print('convergence reached at epoch', epoch+1)
                        break
                    else:
                        old_cost = av_cost

            # testing
            correct_prediction = tf.equal(tf.argmax(model, 1), tf.argmax(y_, 1))
            acc = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            if prnt:
                print('results', end='')
                print((' for model '+str(i+1)+':') if cross_validate else ':')
                print('w =', sess.run(w))
                print('b =', sess.run(b))
                if cross_validate or (not cross_validate and train_prop < 1):
                    print('accuracy:', pt.pc(acc.eval({ x:Xts, y_:Yts }),dec=2))

            models.append({
                'w': sess.run(w),
                'b': sess.run(b),
                'acc': acc.eval({ x: Xts, y_: Yts })
            })

    # get average model from cross-validated set of models.
    if cross_validate:
        av_w = [ [0, 0] for i in range(num_features) ]
        av_b = [0, 0]
        for i in range(len(models)):
            for j in range(num_features):
                av_w[j] += models[i]['w'][j][:2]
            av_b += models[i]['b'][:2]
        for i in range(num_features):
            av_w[i] /= len(models)
        av_b /= len(models)
        average = {
            'w': av_w,
            'b': av_b,
        }
        if prnt:
            print('average model:')
            print('w = [')
            for w in average['w']:
                print('\t', str(w[0])+',', str(w[1])+',')
            print(']')
            print('b = [')
            b = average['b']
            print('\t', str(b[0])+',', str(b[1])+',')
            print(']')
    else:
        average = models[0]

    rk.logreg_model = average
    return average

def linreg ( ppr, cache=None, learning_rate=0.01, epochs=100,
             batch_size=1, num_folds=1, train_prop=0.9, random_weights=False,
             convergence_threshold = 0.0001, exclude_poi=False, prnt=False ):
    # setup
    data = formalise(ppr, cache, exclude_poi=exclude_poi, normalise=False)
    models = []
    cross_validate = num_folds > 1
    regularisation_lambda = 0.01
    check_convergence = convergence_threshold and convergence_threshold > 0
    # just for the benefit of the rankers
    if not rk.means or not rk.stddevs:
        normalise_inputs(data[0], out_means=rk.means, out_stddevs=rk.stddevs)

    # get info about data
    if batch_size is None: batch_size=len(data[0])
    num_features = len(data[0][0])  # the heuristics and rankings describing a page.
    num_samples = len(data[0])      # number of movements between pages.

    # size of training/testing set; do for cross validation if cross_validate.
    if cross_validate:
        num_testing = int(num_samples / num_folds)
        num_training = num_samples - num_testing
    else:
        num_training = int(train_prop * num_samples)
        num_testing = num_samples - num_training

    # Xs & Ys: total inputs and true labels, for all samples.
    Xs = data[0]
    Ys = data[1]

    # define tensorflow graph
    x  = tf.placeholder(tf.float32, [None, num_features])
    y_ = tf.placeholder(tf.float32, [None])

    # model weights
    if random_weights:
        w = tf.Variable(tf.random_normal([num_features, 1]))
        b = tf.Variable(tf.random_normal([1]))
    else:
        w = tf.Variable(tf.zeros([num_features, 1]))
        b = tf.Variable(tf.zeros([1]))

    # construct model
    # model calculates y, to test against y_ for cost. Is essentially y=mx+c.
    model = tf.matmul(x, w) + b
    # our cost function, to see how far from the truth we are:
    cost = tf.reduce_sum(tf.square(model - y_))/(2*num_training)
    # L2 regularisation
    cost = tf.reduce_mean(tf.reduce_mean(cost) + regularisation_lambda*tf.nn.l2_loss(w))
    # our gradient descent optimizer (to minimize cost via. changing w & b):
    gd = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    for i in range(num_folds):
        # split data into training & testing
        # Xtr & Ytr: training set
        Xtr = Xs[:i*num_testing] + Xs[(i+1)*num_testing:]
        Ytr = Ys[:i*num_testing] + Ys[(i+1)*num_testing:]
        # Xts & Yts: testing set
        Xts = Xs[i*num_testing:(i+1)*num_testing]
        Yts = Ys[i*num_testing:(i+1)*num_testing]

        # normalise input sets. use training set's means/standard deviations
        mn = []
        sd = []
        Xtr = normalise_inputs(Xtr, out_means=mn, out_stddevs=sd)
        Xts = normalise_inputs(Xts, in_means=mn, in_stddevs=sd)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            # training cycle
            num_batches = math.ceil(num_training / batch_size)
            bxs = batches(Xtr, batch_size)
            bys = batches(Ytr, batch_size)
            old_cost = None
            for epoch in range(epochs):
                av_cost = 0

                for j in range(num_batches):
                    # perform gradient descent optimisation on model.
                    _, c = sess.run(
                        [gd, cost],
                        feed_dict = { x: bxs[j], y_: bys[j] }
                    )
                    av_cost += c / num_batches

                if prnt and not cross_validate:
                    print('epoch', (epoch+1), 'cost =', av_cost)
                # check for convergence of the model
                if check_convergence:
                    if old_cost and abs(av_cost - old_cost) < convergence_threshold:
                        if prnt: print('convergence reached at epoch', epoch+1)
                        break
                    else:
                        old_cost = av_cost

            # testing
            err = tf.square(model - y_)
            acc = 1 - tf.reduce_mean(tf.cast(err, tf.float32))
            if prnt:
                print('results', end='')
                print((' for model '+str(i+1)+':') if cross_validate else ':')
                print('w =', sess.run(w))
                print('b =', sess.run(b))
                if train_prop < 1:
                    print('accuracy:', pt.pc(acc.eval({ x: Xts, y_: Yts }), dec=2))

            models.append({
                'w': sess.run(w),
                'b': sess.run(b),
                'acc': acc.eval({ x: Xts, y_: Yts })
            })

    # get average model from cross-validated set of models.
    if cross_validate:
        av_w = [ 0 for i in range(num_features) ]
        av_b = [0]
        for model in models:
            for j in range(num_features):
                av_w[j] += model['w'][j]
            av_b += model['b']
        for i in range(num_features):
            av_w[i] /= len(models)
        av_b /= len(models)
        average = {
            'w': av_w,
            'b': av_b,
        }
        if prnt:
            print('average model:\nw = [')
            for w in average['w']:
                print('\t', str(w)+',')
            print(']\nb = [\n\t', average['b'], '\n]')
    else:
        average = models[0]

    rk.linreg_model = average
    return average

def one_hot ( data, num_classes=None ):
    ''' convert a list of class labels (0, 1, 2 etc.) into a list of
    probability distributions where all probabilities are 0, except the true
    value which is 1.
    '''
    oh = []
    if num_classes is None: num_classes = max(data) + 1

    for i in range(len(data)):
        prob_dist = [0] * num_classes
        prob_dist[data[i]] = 1
        oh.append(prob_dist)

    return oh

def batches ( data, batch_size ):
    ''' turn big list of data into a bunch of batches. '''
    bs = batch_size
    nb = math.ceil(len(data)/batch_size)
    return [ data[i*bs:(i+1)*bs] for i in range(nb) ]

def nn ( ppr, cache=None, learning_rate=0.01, epochs=100,
         batch_size=1, num_hidden_layers=5, hidden_layer_size=5, num_folds=1,
         train_prop=0.9, convergence_threshold=0.0001, exclude_poi=False,
         prnt=False ):
    # setup
    data = formalise(ppr, cache, exclude_poi=exclude_poi, normalise=False)
    models = []
    cross_validate = num_folds > 1
    regularisation_lambda = 0.01
    check_convergence = convergence_threshold and convergence_threshold > 0
    # just for the benefit of the rankers
    if not rk.means or not rk.stddevs:
        normalise_inputs(data[0], out_means=rk.means, out_stddevs=rk.stddevs)

    # get info about data
    if batch_size is None: batch_size=len(data[0])
    num_features = len(data[0][0])  # the heuristics and rankings describing a page.
    num_classes = max(data[1])+1    # to choose, or not to choose a page.
    num_samples = len(data[0])      # number of movements between pages.

    # size of training/testing set; do for cross validation if cross_validate.
    if cross_validate:
        num_testing = int(num_samples / num_folds)
        num_training = num_samples - num_testing
    else:
        num_training = int(train_prop * num_samples)
        num_testing = num_samples - num_training

    # Xs & Ys: total inputs and true labels, for all samples.
    Xs = data[0]
    Ys = one_hot(data[1], num_classes)

    # define tensorflow graph
    x  = tf.placeholder(tf.float32, [None, num_features])
    y_ = tf.placeholder(tf.float32, [None, num_classes])

    # define model
    def net ( x, w, b ):
        # TODO - currently using ReLU activation because ???
        activation = tf.nn.relu

        layer_input = x
        for i in range(num_hidden_layers):
            # define the hidden layers, and chain them together
            hidden_layer = activation(tf.matmul(layer_input, w[i]) + b[i])
            layer_input = hidden_layer

        # final layer - linear activation
        output = tf.matmul(layer_input, w[-1]) + b[-1]
        return output

    # model weights
    w = []
    b = []
    previous_size = num_features
    for i in range(num_hidden_layers):
        # initialise weights & biases for hidden layers
        w.append(tf.Variable(tf.random_normal([ previous_size, hidden_layer_size ])))
        b.append(tf.Variable(tf.random_normal([ hidden_layer_size ])))
        previous_size = hidden_layer_size
    # output layer
    w.append(tf.Variable(tf.random_normal([ previous_size, num_classes ])))
    b.append(tf.Variable(tf.random_normal([ num_classes ])))

    # construct model
    # model calculates y, to test against y_ for cost. Is essentially y=mx+c.
    model = net(x, w, b)
    # our cost function, to see how far from the truth we are:
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=model))
    # our optimizer (to minimize cost via. changing w & b):
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    for i in range(num_folds):
        # split data into training & testing
        # Xtr & Ytr: training set
        Xtr = Xs[:i*num_testing] + Xs[(i+1)*num_testing:]
        Ytr = Ys[:i*num_testing] + Ys[(i+1)*num_testing:]
        # Xts & Yts: testing set
        Xts = Xs[i*num_testing:(i+1)*num_testing]
        Yts = Ys[i*num_testing:(i+1)*num_testing]

        # normalise input sets. use training set's means/standard deviations
        mn = []
        sd = []
        Xtr = normalise_inputs(Xtr, out_means=mn, out_stddevs=sd)
        Xts = normalise_inputs(Xts, in_means=mn, in_stddevs=sd)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            # training cycle
            num_batches = math.ceil(num_training / batch_size)
            bxs = batches(Xtr, batch_size)
            bys = batches(Ytr, batch_size)
            old_cost = None
            for epoch in range(epochs):
                av_cost = 0

                for j in range(num_batches):
                    # perform gradient descent optimisation on model.
                    _, c = sess.run(
                        [optimizer, cost],
                        feed_dict = { x: bxs[j], y_: bys[j] }
                    )
                    av_cost += c / num_batches

                if prnt and not cross_validate:
                    print('epoch', (epoch+1), 'cost =', av_cost)
                # check for convergence of the model
                if check_convergence:
                    if old_cost and abs(av_cost - old_cost) < convergence_threshold:
                        if prnt: print('convergence reached at epoch', epoch+1)
                        break
                    else:
                        old_cost = av_cost


            # testing
            correct_prediction = tf.equal(tf.argmax(model, 1), tf.argmax(y_, 1))
            acc = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            if prnt:
                print('results', end='')
                print((' for model '+str(i+1)+':') if cross_validate else ':')
                if train_prop < 1:
                    print('accuracy:', pt.pc(acc.eval({ x: Xts, y_: Yts }), dec=2))

            models.append({
                'w': sess.run(w),
                'b': sess.run(b),
                'acc': acc.eval({ x: Xts, y_: Yts })
            })

    # get average model from cross-validated set of models.
    if cross_validate:
        weights = [ models[i]['w'] for i in range(len(models)) ]
        biases  = [ models[i]['b'] for i in range(len(models)) ]
        av_w = weights[0]
        av_b = biases[0]
        for i in range(1, len(models)):
            for j in range(num_hidden_layers):
                for k in range(len(weights[i][j])):
                    feature = weights[i][j][k]
                    av_w[j][k][0] += feature[0]
                    av_w[j][k][1] += feature[1]
                av_b[j][0] += biases[i][j][0]
                av_b[j][1] += biases[i][j][1]
        for i in range(num_hidden_layers):
            for j in range(len(av_w[i])):
                av_w[i][j][0] /= len(models)
                av_w[i][j][1] /= len(models)
            av_b[0][i] /= len(models)
            av_b[1][i] /= len(models)
        average = {
            'w': av_w,
            'b': av_b,
        }
    else:
        average = models[0]

    if prnt:
        print('final net:')
        print('w:')
        for weight in average['w']:
            print(weight)
        print('b:')
        for bias in average['b']:
            print(bias)

    rk.net_model = average
    return average
