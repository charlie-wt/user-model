#import sys, os
#sys.path.append(os.path.join(sys.path[0], "models"))

import heuristics as hs
import ls
import printer as pt

import numpy
import math
import random

'''
ranker

take visible pages, and return probability distribution of them for which page
to choose via one of the functions. output to be given to some decider function.
'''

prnt=False

manual_heuristics = {
    'w': [
         -5.00000,          # walk dist
        -10.00000,          # visits
         -0.05000,          # alt
#         0.10000,          # poi
          0.05000,          # mention
        -50.00000,          # ranking - walk dist
        -10.00000,          # ranking - visits
         -0.10000,          # ranking - alt
#        -0.15000,          # ranking - poi
         -0.30000           # ranking - mention
    ],
    'b': 0.00000
}

# for internal use by ml and ranker functions
logreg_model = {}
linreg_model = {}
net_model = {}
means = []
stddevs = []

def rand ( user, story, pages, cache=None ):
    ''' random. '''
    prob = 1 / len(pages)
    options = {}
    for i in range(len(pages)):
        options[pages[i]] = prob
    return options

def rank_by ( heuristic, inverse=False, no_loops=False ):
    ''' rank using a heuristic. '''
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
    ''' shortest straight line distance. '''
    fn = rank_by(hs.distance, True, False)
    return fn(user, story, pages, cache)

def walk_dist ( user, story, pages, cache=None ):
    ''' shortest walking distance, via roads. '''
    fn = rank_by(hs.walk_dist, True, False)
    return fn(user, story, pages, cache)

def visits ( user, story, pages, cache=None ):
    ''' prefer the least visited page. '''
    fn = rank_by(hs.visits, True, False)
    return fn(user, story, pages, cache)

def alt ( user, story, pages, cache=None ):
    ''' prefer to go downhill. '''
    fn = rank_by(hs.altitude, True, False)
    return fn(user, story, pages, cache)

def poi ( user, story, pages, cache=None ):
    ''' prefer pages with more nearby points of interest. '''
    fn = rank_by(hs.points_of_interest, False, False)
    return fn(user, story, pages, cache)

def mentioned ( user, story, pages, cache=None ):
    ''' prefer pages with names mentioned more by the current page's text. '''
    fn = rank_by(hs.mentioned, False, False)
    return fn(user, story, pages, cache)

def logreg ( user, story, pages, cache=None ):
    ''' use logistic regression model to predict the page to choose. '''
    import ml
    model = logreg_model
    if not model: raise ValueError('Please initialise regression parameters.')
    name = user.page().name if user.page() else '--start--'
    if prnt: print('options from', name+':')

    choices = pages
    inputs = ml.make_input(story, user, choices, cache, True)

    # apply regression
    results = []
    idx = 1
    for x in inputs:
        # y = w*x + b
        yes = sum([ x[i]*model['w'][i][1] for i in range(len(x)) ])
        yes += model['b'][1]
        no = sum([ x[i]*model['w'][i][0] for i in range(len(x)) ])
        no += model['b'][0]
        output = yes - no
        results.append(output)

    # get rid of negative values - they mess up the softmax :(
    smallest = abs(min(results))
    for i in range(len(results)):
        results[i] += smallest

    # normalise (softmax)
    factor = 1 / sum(results) if sum(results) != 0 else 1
    chances = [ r * factor for r in results ]

    # avoid having only 0.0 chance for everything
    if chances == [0] * len(chances):
        equal_chance = 1 / len(chances)
        chances = [equal_chance] * len(chances)

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
    ''' use linear regression model to predict the page to choose. '''
    import ml
    model = linreg_model
    if not model: raise ValueError('Please initialise regression parameters.')
    if prnt:
        name = user.page().name if user.page() else '--start--'
        print('options from', name+':')

    # get inputs in proper form
    choices = pages
    inputs = ml.make_input(story, user, choices, cache, exclude_poi=False)
    inputs = ml.normalise_inputs(inputs, in_means=means, in_stddevs=stddevs)

    # apply regression
    results = []
    for x in inputs:
        # y = w*x + b
        output = sum([ x[i]*model['w'][i] for i in range(len(x)) ])
        output += model['b']
        results.append(float(output))

    # get rid of negative values - they mess up the softmax :(
    if min(results) < 0:
        lowest = abs(min(results))
        for i in range(len(results)):
            results[i] += lowest

    # normalise (softmax)
    factor = 1 / sum(results) if sum(results) != 0 else 1
    chances = [ r * factor for r in results ]

    # avoid having 0.0 chance for everything
    if chances == [0] * len(chances):
        equal_chance = 1 / len(chances)
        chances = [equal_chance] * len(chances)

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
    ''' use neural network model to predict the page to choose. '''
    import ml
    import numpy as np
    model = net_model
    if not model: raise ValueError('Please initialise neural network.')
    name = user.page().name if user.page() else '--start--'
    if prnt: print('options from', name+':')

    choices = pages
    inputs = ml.make_input(story, user, choices, cache, True)

    # apply neural network
    results = []
    idx = 1
    for p in inputs:
        prediction = _net(np.array(p), np.array(model['w']), np.array(model['b']))
        yes = prediction[1]
        no = prediction[0]
        output = yes - no
        results.append(output)

    # get rid of negative values - we're just taking the max anyway, and they mess things up :(
    smallest = abs(min(results))
    for i in range(len(results)):
        results[i] += smallest

    # normalise (softmax)
    factor = 1 / sum(results) if sum(results) != 0 else 1
    chances = [ r * factor for r in results ]

    # avoid having only 0.0 chance for everything
    if chances == [0] * len(chances):
        equal_chance = 1 / len(chances)
        chances = [equal_chance] * len(chances)

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

    return inputs

def _net ( x, w, b ):
    ''' run a neural net (defined by the weight & bias arrays) on an input. '''
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
