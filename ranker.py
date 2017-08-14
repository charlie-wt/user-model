import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import location as l
import page
import heuristics as hs
import ls

import math
import random

###### ranker ################
# take visible pages, and return probability distribution of them for which
# page to choose via one of the functions. output to be given to some decider
# function.
##############################

reg = {
    'w': [[ 29.25730515, -29.25730515],
          [  0.,           0.        ],
          [-22.56334496,  22.56334496],
          [-21.10176659,  21.10176849],
          [  1.42525840,  -1.42525840],
          [ -1.38244212,   1.38244212],
          [ -0.98336744,   0.9833675 ],
          [ -1.03950977,   1.03950977],
          [ -0.86692393,   0.86692399],
          [ -1.24961233,   1.24961233]],
    'b': [-2.63376451,  2.63376451]
}
reg_no_poi = {
    'w': [[  5.54028082,  -5.54027319],
          [  0.,           0.        ],
          [-15.39587307,  15.39587307],
          [  0.51478320,  -0.51478308],
          [ -3.04297018,   3.04297018],
          [ -2.10439253,   2.10439229],
          [ -1.71184516,   1.71184516],
          [ -6.63762236,   6.63762283]],
    'b': [-0.4354198,   0.43541986]
}

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
        by_h_val = sorted(choices, key = lambda p : h_values[pages.index(p)])
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

        # normalise
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

    inputs = ml.make_input(story, user, pages, cache, True)

    # apply regression
    results = []
    idx = 1
    for p in inputs:
        # y = w*x + b
        output = sum([ p[i]*reg_no_poi['w'][i][idx] for i in range(len(p)) ])
        output += reg_no_poi['b'][idx]
        results.append(output)

    # normalise
    factor = 1 / sum(results) if sum(results) != 0 else 1
    chances = [ r * factor for r in results ]

    # gen dictionary
    options = {}
    for i in range(len(pages)):
        options[pages[i]] = chances[i]
    return options
