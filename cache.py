from collections import defaultdict

# a dictionary that automatically creates keys if they don't exist, deeply
cache = lambda: defaultdict(cache)
