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
    # score pages
    distances = [hs.distance(p, user, story, cache) for p in pages]
    by_distance = sorted(pages, key = lambda p : distances[pages.index(p)])
    distances.sort()
    chances = []
    for i in range(len(by_distance)):
        chances.append(1 / distances[i] if distances[i] != 0 else 1)
    # normalise
    factor = 1 / sum(chances)
    chances = [ c * factor for c in chances ]
    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options

def walk_dist ( user, story, path, pages, cache=None ):
# shortest walking distance, via roads
    if len(pages) == 1: return { pages[0] : 1 }
    # score pages
    distances = [hs.walk_dist(p, user, story, cache) for p in pages]
    by_distance = sorted(pages, key = lambda p : distances[pages.index(p)])
    distances.sort()
    chances = []
    for i in range(len(by_distance)):
        chances.append(1 / distances[i] if distances[i] != 0 else 1)

    # optionally eliminate visited nodes
    for i in range(len(chances)):
        if hs.visits(by_distance[i], path) != 0: chances[i] = 0

    # normalise
    factor = 1 / sum(chances)
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
    distances = [hs.distance(p, user, story) for p in pages]
    by_distance = sorted(pages, key = lambda p : distances[pages.index(p)])
    distances.sort()
    chances = []

    # closer = better
    for i in range(len(by_distance)):
        chance = 1 / distances[i] if distances[i] != 0 else 1
        chances.append(chance)

    # visited before = worse
    factor = 0.0  # multiply prob of page by this for every previous visit
    for i in range(len(by_distance)):
        chances[i] = chances[i] * (factor)**hs.visits(by_distance[i], path)

    # normalise
    factor = 1 / sum(chances)
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options
