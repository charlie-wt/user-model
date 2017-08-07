import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import re
import time

from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError
import json

import overpy

import location as l
import ls
import mapping as mp
import printer as pt

##### heuristics #############
# a set of functions by which to judge a page's appealingness. To be used in
# ranking algorithms, primarily.
##############################

def distance ( page, user, story, cache=None ):
# straight line distance from user -> page.
    prnt=False
    page_loc = page.getLoc(story)
    us_page = user.page()

    # if next page has no location, dist = 0
    if page_loc is None:
        return 0
    else:
        # if current page has no location, we can't use the cache
        if us_page is None or us_page.getLoc(story) is None:
            return l.metres(user.loc, page_loc)
        elif cache is not None:
            # use the cache
            if page.id in cache['distance'][us_page.id]:
                if prnt: print(us_page.name, "->", page.name, "is cached.")
                return cache['distance'][us_page.id][page.id]
            elif us_page.id in cache['distance'][page.id]:
                if prnt: print(us_page.name, "->", page.name, "is cached.")
                return cache['distance'][page.id][us_page.id]
    # make a new entry
    dist = l.metres(us_page.getLoc(story), page_loc)
    if cache is not None: cache['distance'][us_page.id][page.id] = dist
    return dist

def visits ( page, path ):
# has the user visited this node before?
    return ls.count(path, page.id)

def walk_dist ( page, user, story, cache=None ):
# walking distance, via roads (osrm).
    prnt=False
    page_loc = page.getLoc(story)
    us_page = user.page()

    # if next page has no location, dist = 0
    if page_loc is None:
        return 0
    else:
        # if current page has no location, we can't use the cache
        if us_page is None or us_page.getLoc(story) is None:
            return mp.dist(user.loc, page_loc)
        elif cache is not None:
            # use the cache
            if page.id in cache['walk_dist'][us_page.id]:
                if prnt: print(us_page.name, "->", page.name, "is cached.")
                return cache['walk_dist'][us_page.id][page.id]
            elif us_page.id in cache['walk_dist'][page.id]:
                if prnt: print(us_page.name, "->", page.name, "is cached.")
                return cache['walk_dist'][page.id][us_page.id]
    # make a new entry
    dist = mp.dist(us_page.getLoc(story), page_loc)
    if cache is not None: cache['walk_dist'][us_page.id][page.id] = dist
    if prnt: print(us_page.name, "->", page.name, "=", dist)
    return dist

def altitude ( page, user, story, cache=None ):
# altitude of page
    prnt=False
    page_loc = page.getLoc(story)
    if page_loc is None:
        if prnt: print(page.name, "can be accessed from anywhere.")
        return mp.alt(user.loc)
    if cache is not None and page.id in cache['altitude']:
        if prnt: print("altitude of", page.name, "is cached (" \
                       +str(cache['altitude'][page.id])+").")
        return cache['altitude'][page.id]
    alt = mp.alt(page_loc)
    if cache is not None: cache['altitude'][page.id] = alt
    if prnt: print("altitude of", page.name, "is", alt)
    return alt

def points_of_interest ( page, user, story, cache=None ):
# get the number of points of interest near a page
    prnt=True
    page_loc = page.getLoc(story)
    if page_loc is None: page_loc = user.loc

    if cache is not None and page.id in cache['poi']:
        if prnt: print(page.name, "is cached with", cache['poi'][page.id], "pois.")
        return cache['poi'][page.id]

    try:
        poi = mp.poi(page_loc)
    except overpy.exception.OverpassTooManyRequests:
        # TODO - something better than this.
        print(page.name, "- too many overpass requests. waiting 15 seconds to continue.")
        poi = 0
        time.sleep(15)
        return poi
    if cache is not None: cache['poi'][page.id] = poi
    if prnt: print(page.name, "is near", poi, "points of interest.")
    return poi

def points_of_interest_alt ( page, user, story, cache=None ):
# get the number of points of interest near a page
    # alternate: doesn't use overpy library -> more flexibility
    prnt=True
    page_loc = page.getLoc(story)
    if page_loc is None: page_loc = user.loc

    if cache is not None and page.id in cache['poi']:
        if prnt: print(page.name, "is cached with", cache['poi'][page.id], "pois.")
        return cache['poi'][page.id]

    url = "http://overpass-api.de/api/interpreter"
    query = 'data=[out:json];('
    around = '(around:'+str(100)+','+str(page_loc[0])+','+str(page_loc[1])+')'
    for f in mp.features:
        feature = '['+f+'~\"'
        values = ''
        for v in mp.features[f]:
            values += v+'|'
        values = values[:-1]
        feature += values + '\"];'
        query += 'node'+around+feature
        query += 'way'+around+feature
#        query += 'rel'+around+feature
    query += ');out count;'

    # TODO - NOT SURE THAT THIS BIT WORKS WITH TIMEOUTS AND STUFF
    try:
        f = urlopen(url, query.encode('utf-8'))
    except HTTPError as e:
        f = e
    response = None
    while(True):
        response = f.read(4096)
        if f.code == 200: break
        print('overpass too many queries - retrying in 15 seconds.')
        time.sleep(15)
    f.close()

    json_data = json.loads(response.decode('utf-8'))
    poi = int(json_data['elements'][0]['tags']['total'])

    if cache is not None: cache['poi'][page.id] = poi
    if prnt: print(page.name, "is near", poi, "points of interest.")
    return poi

def mentioned ( page, user, story, cache=None ):
# how much the title of 'page' is mentioned by the text of the previous page.
    # use tf-idf (term frequency, inverse document frequency) for this.
    us_page = user.page()
    prnt=False

    if us_page is None:
        return 0
    elif cache is not None and page.id in cache['mentioned'][us_page.id]:
        if prnt: print(us_page.name, "->", page.name, "is cached.")
        return cache['mentioned'][us_page.id][page.id]

    title = page.name.lower().split()
    title = [ re.sub('[\W_]+', '', w) for w in title ]
    current = us_page.name.lower().split() + us_page.text.lower().split()
    current = [ re.sub('[\W_]+', '', w) for w in current ]

    tf = { w: 0 for w in title }
    for w in current:
        if w in title:
            tf[w] += 1

    tfidf = {}
    for t in tf:
        tfidf[t] = tf[t] * story.idf(t)
    score = sum(tfidf.values())

    if prnt:
        print(score, 'matches for', page.name+':')
        for t in tfidf:
            print(tf[t], "->", pt.fmt(tfidf[t],1), ':', t)

    if cache is not None:
        cache['mentioned'][us_page.id][page.id] = score
    return score
