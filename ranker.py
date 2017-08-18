#import sys, os
#sys.path.append(os.path.join(sys.path[0], "models"))

import heuristics as hs
import ls
import printer as pt

import numpy
import math
import random

###### ranker ################
# take visible pages, and return probability distribution of them for which
# page to choose via one of the functions. output to be given to some decider
# function.
##############################

prnt=False

net = {}
reg_lin_no_poi = {}
reg = {}
reg_no_poi = {}

def rand ( user, story, pages, cache=None ):
# random
    prob = 1 / len(pages)
    options = {}
    for i in range(len(pages)):
        options[pages[i]] = prob
    return options

def rank_by ( heuristic, inverse=False, no_loops=False ):
# rank using a heuristic
    def rank ( user, story, pages, cache=None ):
        # possibly only deal with pages not previously visited
        choices = pages
        if no_loops:
            choices = [ p for p in pages if hs.visits(p, user) == 0 ]

        # score pages by value output by heuristic (by default low -> high)
        h_values = [ heuristic(p, user, story, cache) for p in choices ]
        by_h_val = sorted(choices, key = lambda p : h_values[choices.index(p)])
        h_values.sort()
        chances = []
        if inverse:
            highest = h_values[-1]
            lowest = h_values[0]
            for i in range(len(by_h_val)):
                chances.append((highest - h_values[i]) + abs(lowest))
        else:
            chances = h_values

        # if all vals = 0, just give an equal chance to everything
        if h_values == [ 0 ] * len(h_values):
            return rand(user, story, pages, cache)

        # normalise (softmax)
        factor = 1 / sum(chances) if sum(chances) != 0 else 1
        chances = [ c * factor for c in chances ]

        # gen dictionary
        options = {}
        for i in range(len(by_h_val)):
            options[by_h_val[i]] = chances[i]
        if no_loops:
            for p in [ p for p in pages if p not in options ]:
                options[p] = 0
        return options
    return rank

def dist ( user, story, pages, cache=None ):
# shortest straight line distance
    fn = rank_by(hs.distance, True, True)
    return fn(user, story, pages, cache)

def walk_dist ( user, story, pages, cache=None ):
# shortest walking distance, via roads
    fn = rank_by(hs.walk_dist, True, True)
    return fn(user, story, pages, cache)

def visits ( user, story, pages, cache=None ):
# prefer the least visited page
    fn = rank_by(hs.visits, True, True)
    return fn(user, story, pages, cache)

def alt ( user, story, pages, cache=None ):
# prefer to go downhill
    fn = rank_by(hs.altitude, True, True)
    return fn(user, story, pages, cache)

def poi ( user, story, pages, cache=None ):
# prefer pages with more nearby points of interest
    fn = rank_by(hs.points_of_interest, False, True)
    return fn(user, story, pages, cache)

def mentioned ( user, story, pages, cache=None ):
# prefer pages with names mentioned more by the current page's text.
    fn = rank_by(hs.mentioned, False, True)
    return fn(user, story, pages, cache)

def logreg ( user, story, pages, cache=None ):
# use logistic regression model to predict the page to choose.
    import ml
    if reg is None: raise ValueError('Please initialise regression parameters.')
    name = user.page().name if user.page() else '--start--'
    if prnt: print('options from', name+':')

    choices = pages
#    choices = [ p for p in pages if hs.visits(p, user) == 0 ]

#    inputs = ml.normalise_inputs(ml.make_input(story, user, choices, cache, True))
    inputs = ml.make_input(story, user, choices, cache, True)

    # apply regression
    results = []
    idx = 1
    for p in inputs:
        # y = w*x + b
        # TODO - perhaps instead of just using the 'yes' amount, do yes - no?
        #        Then even if both are high, you don't end up thinking the page
        #        is too desirable.
        yes = sum([ p[i]*reg_no_poi['w'][i][1] for i in range(len(p)) ])
        yes += reg_no_poi['b'][1]
        no = sum([ p[i]*reg_no_poi['w'][i][0] for i in range(len(p)) ])
        no += reg_no_poi['b'][0]
        output = yes - no
        results.append(output)

    # get rid of negative values - we're just taking the max anyway, and they mess things up :(
    for i in range(len(results)):
        results[i] += abs(min(results))

    # normalise (softmax)
    factor = 1 / sum(results) if sum(results) != 0 else 1
    chances = [ r * factor for r in results ]

    if prnt:
        for i in range(len(choices)):
            name = choices[i].name if choices[i] else '---'
            print('\t', pt.fmt(results[i], dec=2), '->', pt.pc(chances[i]), ':', name)

    # gen dictionary
    options = {}
    for i in range(len(choices)):
        options[choices[i]] = chances[i]
    for p in [ p for p in pages if p not in options ]:
        options[p] = 0
    return options

def linreg ( user, story, pages, cache=None ):
# use logistic regression model to predict the page to choose.
    import ml
    if reg is None: raise ValueError('Please initialise regression parameters.')
    name = user.page().name if user.page() else '--start--'
    if prnt: print('options from', name+':')

    choices = pages
#    choices = [ p for p in pages if hs.visits(p, user) == 0 ]

#    inputs = ml.normalise_inputs(ml.make_input(story, user, choices, cache, True))
    inputs = ml.make_input(story, user, choices, cache, True)

    # apply regression
    results = []
    idx = 1
    for p in inputs:
        # y = w*x + b
        output = sum([ p[i]*reg_lin_no_poi['w'][i] for i in range(len(p)) ])
        output += reg_lin_no_poi['b']
        results.append(float(output))

    # get rid of negative values - we're just taking the max anyway, and they mess things up :(
    for i in range(len(results)):
        results[i] += abs(min(results))

    # normalise (softmax)
    factor = 1 / sum(results) if sum(results) != 0 else 1
    chances = [ r * factor for r in results ]

    if prnt:
        for i in range(len(choices)):
            name = choices[i].name if choices[i] else '---'
            print('\t', pt.fmt(results[i], dec=2), '->', pt.pc(chances[i]), ':', name)

    # gen dictionary
    options = {}
    for i in range(len(choices)):
        options[choices[i]] = chances[i]
    for p in [ p for p in pages if p not in options ]:
        options[p] = 0
    return options

def nn ( user, story, pages, cache=None ):
# use logistic regression model to predict the page to choose.
    import ml
    import numpy as np
    if reg is None: raise ValueError('Please initialise regression parameters.')
    name = user.page().name if user.page() else '--start--'
    if prnt: print('options from', name+':')

    choices = pages
#    choices = [ p for p in pages if hs.visits(p, user) == 0 ]

#    inputs = ml.normalise_inputs(ml.make_input(story, user, choices, cache, True))
    inputs = ml.make_input(story, user, choices, cache, True)

    # apply regression
    results = []
    idx = 1
    for p in inputs:
        prediction = _net(np.array(p), np.array(net['w']), np.array(net['b']))
#        print('prediction:', prediction)
        yes = prediction[1]
        no = prediction[0]
        output = yes - no
        results.append(output)

    # get rid of negative values - we're just taking the max anyway, and they mess things up :(
    for i in range(len(results)):
        results[i] += abs(min(results))

    # normalise (softmax)
    factor = 1 / sum(results) if sum(results) != 0 else 1
    chances = [ r * factor for r in results ]

    if prnt:
        for i in range(len(choices)):
            name = choices[i].name if choices[i] else '---'
            print('\t', pt.fmt(results[i], dec=2), '->', pt.pc(chances[i]), ':', name)

    # gen dictionary
    options = {}
    for i in range(len(choices)):
        options[choices[i]] = chances[i]
    for p in [ p for p in pages if p not in options ]:
        options[p] = 0
    return options

def _net ( x, w, b ):
# run a neural net (defined by the weight & bias arrays) on an input
    import numpy as np

    num_hidden_layers = len(b) - 1
    neuron = lambda x, w, b: x.dot(w) + b      # y = wx + b
    activation = lambda n: np.maximum(n, 0)    # ReLU

    layer_input = x
    for i in range(num_hidden_layers):
        # define the hidden layers, and chain them together
        hidden_layer = activation(neuron(layer_input, w[i], b[i]))
#        print('max(0,', neuron(layer_input, w[i], b[i]), ') =', hidden_layer)
        layer_input = hidden_layer

    # final layer - linear activation
#    output = activation(neuron(layer_input, w[-1], b[-1]))
    output = neuron(layer_input, w[-1], b[-1])

    return output
