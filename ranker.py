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

def dist ( user, story, path, pages, cache=None ):
# shortest straight line distance
    choices = [ p for p in pages if hs.visits(p, path) == 0 ]
    if len(choices) == 1: return { choices[0] : 1 }

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
        return rand(user, story, path, choices, cache)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options

def walk_dist ( user, story, path, pages, cache=None ):
# shortest walking distance, via roads
    choices = [ p for p in pages if hs.visits(p, path) == 0 ]
    if len(choices) == 1: return { choices[0] : 1 }

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
        return rand(user, story, path, choices, cache)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options

def rand ( user, story, path, pages, cache=None ):
# random
    prob = 1 / len(pages)
    options = {}
    for i in range(len(pages)):
        options[pages[i]] = prob
    return options

def guess ( user, story, path, pages, cache=None ):
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
        chances[i] = chances[i] * (factor)**hs.visits(by_distance[i], path)

    # normalise
    factor = 1 / sum(chances) if sum(chances) != 0 else 1
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options

def alt ( user, story, path, pages, cache=None ):
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

def poi ( user, story, path, pages, cache=None ):
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

def mentioned ( user, story, path, pages, cache=None ):
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
