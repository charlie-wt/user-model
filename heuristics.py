import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import location as l
import ls
import mapping as mp

##### heuristics #############
# a set of functions by which to judge a page's appealingness. To be used in
# ranking algorithms, primarily.
##############################

def distance ( page, user, story ):
# straight line distance from user -> page.
    page_loc = page.getLoc(story)
    if page_loc is None: page_loc = user.loc
    return l.metres(user.loc, page_loc)

def visits ( page, path ):
# has the user visited this node before?
    return ls.count(path, page.id)

def gdist ( page, user, story ):
# walking distance, via roads (google maps api).
    page_loc = page.getLoc(story)
    if page_loc is None: page_loc = user.loc
    return mp.gdist(user.loc, page_loc)

def osmdist ( page, user, story):
# walking distance, via roads (pyroutelib + openstreetmap).
    page_loc = page.getLoc(story)
    if page_loc is None: page_loc = user.loc
    return mp.osmdist(user.loc, page_loc)

def osrmdist ( page, user, story):
# walking distance, via roads (osrm).
    page_loc = page.getLoc(story)
    if page_loc is None: page_loc = user.loc
    return mp.osrmdist(user.loc, page_loc)
