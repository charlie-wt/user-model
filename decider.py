import math
import random

def distance ( curr, ns ):
    mindist = float('inf')
    minidx = -1
    for n in ns:
        d = graph.dist(curr, n)
        if ( d < mindist ):
            mindist = d
            minidx = ns.index(n)
    return minidx

def rand ( curr, ns ):
    return math.floor(random.random() * len(ns))
