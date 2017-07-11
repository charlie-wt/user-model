import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import location as l
import page
import heuristics as hs

import ls
import math
import random

def dist ( user, story, path, pages ):
# shortest straight line distance
    mindist = float('inf')
    minidx = -1
    for page in pages:
        page_loc = page.getLoc(story)
        if page_loc == None: page_loc = user.loc
        d = l.metres(user.lat(), user.lon(), page_loc[0], page_loc[1])
        if ( d < mindist ):
            mindist = d
            minidx = pages.index(page)
    return minidx

def rand ( user, story, path, pages ):
# random
    return math.floor(random.random() * len(pages))

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

    # scale chances to be /1
    chances = [c / sum(chances) for c in chances]

    # choose random number, use to choose page
    choice = random.random()
    acc = 0
    by_prob = sorted(by_distance, key = lambda p : chances[by_distance.index(p)])
    chances.sort()

    print("comparing", choice, "against")
    for i in range(0, len(by_prob)):
        print(by_prob[i].name, ":", chances[i])
    print("---")

    for i in range(0, len(by_prob)):
        acc = acc + chances[i]
        if choice < acc:
            return pages.index(by_prob[i])

    print("oh no")
    return pages.index(by_distance[0])
