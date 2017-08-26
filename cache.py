from collections import defaultdict

'''
cache

for storing heuristic values so that they need not be recalculated.

internally, is just a dictionary that automatically creates keys if they don't
exist, deeply.
'''

cache = lambda: defaultdict(cache)
