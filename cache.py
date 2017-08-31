from collections import defaultdict

'''
cache

for storing heuristic values so that they need not be recalculated.

internally, is just a dictionary that automatically creates keys if they don't
exist, deeply.
'''

Cache = lambda: defaultdict(Cache)

def merge ( caches, prnt=False ):
    ''' put N caches together. '''
    def recurse ( ch1, ch2, path='cache' ):
        for key, value in ch2.items():
            if type(value) is defaultdict:
                recurse(ch1[key], value, path+'['+str(key)+']')
            else:
                if prnt: print('adding', key, ':', value, 'to', path)
                ch1[key] = value

    new = caches[0].copy()
    for cache in list(caches[1:]):
        recurse(new, cache)
    return new
