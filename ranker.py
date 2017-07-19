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

def dist ( user, story, path, pages ):
# shortest straight line distance
    # score pages
    distances = [hs.distance(p, user, story) for p in pages]
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

def rand ( user, story, path, pages ):
# random
    prob = 1 / len(pages)
    options = {}
    for i in range(len(pages)):
        options[pages[i]] = prob
    return options

def guess ( user, story, path, pages ):
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
    for i in range(len(by_distance)):
        chances[i] = chances[i] * (0.1)**hs.visits(by_distance[i].id, path)

    # normalise
    factor = 1 / sum(chances)
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options
