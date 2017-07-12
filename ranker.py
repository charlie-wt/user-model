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
    for i in range(0, len(by_distance)):
        chances.append(1 / distances[i] if distances[i] != 0 else 1)
    # normalise
    factor = 1 / sum(chances)
    chances = [ c * factor for c in chances ]
    # gen dictionary
    options = {}
    for i in range(0, len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options

def rand ( user, story, path, pages ):
# random
    choice = math.floor(random.random() * len(pages))
    options = {}
    for i in range(0, len(pages)):
        options[pages[i]] = 1 if i == choice else 0
    return options

def guess ( user, story, path, pages ):
# fairly arbitrary guess based on heuristics
    distances = [hs.distance(p, user, story) for p in pages]
    by_distance = sorted(pages, key = lambda p : distances[pages.index(p)])
    distances.sort()
    chances = []

    # closer = better
    for i in range(0, len(by_distance)):
        chance = 1 / distances[i] if distances[i] != 0 else 1
        chances.append(chance)

    # visited before = worse
    for i in range(0, len(by_distance)):
        if hs.visited_before(by_distance[i], path):
            chances[i] = chances[i]/2

    # normalise
    factor = 1 / sum(chances)
    chances = [ c * factor for c in chances ]

    # gen dictionary
    options = {}
    for i in range(0, len(by_distance)):
        options[by_distance[i]] = chances[i]
    return options