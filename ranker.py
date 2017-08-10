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

def dist ( user, story, pages, cache=None ):
# shortest straight line distance
    choices = [ p for p in pages if hs.visits(p, user) == 0 ]
    if len(choices) == 1:
        options = { p: 0 for p in pages }
        options[choices[0]] = 1
        return options

    # score pages
    distances = [hs.distance(p, user, story, cache) for p in choices]
    by_distance = sorted(choices, key = lambda p : distances[choices.index(p)])
    distances.sort()
    chances = []
    furthest = distances[-1]
    closest = distances[0]
    for i in range(len(by_distance)):
        chances.append((furthest - distances[i]) + abs(closest))

    # if all dists = 0, just give an equal chance to everything
    if distances == [ 0 ] * len(distances):
        return rand(user, story, pages, cache)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    for p in [ p for p in pages if p not in options ]:
        options[p] = 0
    return options

def walk_dist ( user, story, pages, cache=None ):
# shortest walking distance, via roads
    choices = [ p for p in pages if hs.visits(p, user) == 0 ]
    if len(choices) == 1:
        options = { p: 0 for p in pages }
        options[choices[0]] = 1
        return options

    # score pages
    distances = [hs.walk_dist(p, user, story, cache) for p in choices]
    by_distance = sorted(choices, key = lambda p : distances[choices.index(p)])
    distances.sort()
    chances = []
    furthest = distances[-1]
    closest = distances[0]
    for i in range(len(by_distance)):
        chances.append((furthest - distances[i]) + abs(closest))

    # if all dists = 0, just give an equal chance to everything
    if distances == [ 0 ] * len(distances):
        return rand(user, story, pages, cache)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    for p in [ p for p in pages if p not in options ]:
        options[p] = 0
    return options

def visits ( user, story, pages, cache=None ):
# go to the least visited page
    if len(pages) == 1: return { pages[0] : 1 }

    # score pages
    num_visits = [ hs.visits(p, user) for p in pages ]
    by_visits = sorted(pages, key = lambda p : num_visits[pages.index(p)])
    num_visits.sort()
    chances = []
    most = num_visits[-1]
    least = num_visits[0]
    for i in range(len(by_visits)):
        chances.append((most - num_visits[i]) + abs(least))

    # if all num visits = 0, just give an equal chance to everything
    if num_visits == [ 0 ] * len(num_visits):
        return rand(user, story, pages, cache)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_visits)):
        options[by_visits[i]] = chances[i]
    return options

def rand ( user, story, pages, cache=None ):
# random
    prob = 1 / len(pages)
    options = {}
    for i in range(len(pages)):
        options[pages[i]] = prob
    return options

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

def alt ( user, story, pages, cache=None ):
# prefer to go downhill (not a very useful ranker on its own)
    alts = [ hs.altitude(p, user, story, cache) for p in pages ]
    by_alt = sorted(pages, key = lambda p : alts[pages.index(p)])
    alts.sort()
    chances = []
    highest = alts[-1]
    lowest = alts[0]

    # lower = better
    for i in range(len(by_alt)):
        chance = (highest - alts[i]) + abs(lowest)
        chances.append(chance)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_alt)):
        options[by_alt[i]] = chances[i]
    return options

def poi ( user, story, pages, cache=None ):
# prefer pages with more nearby points of interest
    # get sorted (low -> high) list of pages by poi count.
    pois = [ hs.points_of_interest(p, user, story, cache) for p in pages ]
    by_poi = sorted(pages, key = lambda p : pois[pages.index(p)])
    pois.sort()
    chances = []

    # normalise
    factor = 1 / sum(pois) if sum(pois) != 0 else 1
    chances = [ c * factor for c in pois ]

    # gen dictionary
    options = {}
    for i in range(len(by_poi)):
        options[by_poi[i]] = chances[i]
    return options

def mentioned ( user, story, pages, cache=None ):
# prefer pages with names mentioned more by the current page's text.
    # get sorted (low -> high) list of pages by mentions.
    mentions = [ hs.mentioned(p, user, story, cache) for p in pages ]
    by_mentions = sorted(pages, key = lambda p : mentions[pages.index(p)])
    mentions.sort()
    chances = []

    # normalise
    factor = 1 / sum(mentions) if sum(mentions) != 0 else 1
    chances = [ c * factor for c in mentions ]

    # gen dictionary
    options = {}
    for i in range(len(by_mentions)):
        options[by_mentions[i]] = chances[i]
    return options

def rank_by ( heuristic, inverse=False, no_loops=False ):
# rank using a heuristic
    def rank ( user, story, pages, cache=None ):
        choices = pages
        if no_loops:
            choices = [ p for p in pages if hs.visits(p, user) == 0 ]

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

def rb_wd ( user, story, pages, cache=None ):
    fn = rank_by(hs.walk_dist, True, True)
    return fn(user, story, pages, cache)

def rb_d ( user, story, pages, cache=None ):
    fn = rank_by(hs.distance, True, True)
    return fn(user, story, pages, cache)

def rb_alt ( user, story, pages, cache=None ):
    fn = rank_by(hs.altitude, True, True)
    return fn(user, story, pages, cache)

def rb_v( user, story, pages, cache=None ):
    fn = rank_by(hs.visits, True, True)
    return fn(user, story, pages, cache)

def rb_poi ( user, story, pages, cache=None ):
    fn = rank_by(hs.points_of_interest, False, True)
    return fn(user, story, pages, cache)

def rb_m ( user, story, pages, cache=None ):
    fn = rank_by(hs.mentioned, False, True)
    return fn(user, story, pages, cache)
