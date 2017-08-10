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

def guess ( user, story, pages, cache=None ):
# TODO - fairly incomplete, needs to be updated/improved.
# fairly arbitrary guess based on heuristics
    distances = [hs.distance(p, user, story, cache) for p in pages]
    by_distance = sorted(pages, key = lambda p : distances[pages.index(p)])
    distances.sort()
    chances = []
    furthest = distances[-1]
    closest = distances[0]

    # closer = better
    for i in range(len(by_distance)):
        chance = (furthest - distances[i]) + abs(closest)
        chances.append(chance)

    # visited before = worse
    factor = 0.0
    for i in range(len(by_distance)):
        chances[i] = chances[i] * (factor)**hs.visits(by_distance[i], user)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options
