import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import location as l

##### heuristics #############
# a set of functions by which to judge a page's appealingness. To be used in
# ranking algorithms, primarily.
##############################

def distance ( page, user, story ):
# straight line distance from user -> page.
    page_loc = page.getLoc(story)
    if page_loc is None: page_loc = user.loc
    return l.metres(user.lat(), user.lon(), page_loc[0], page_loc[1])

def visited_before ( page, path ):
# has the user visited this node before?
    return page in path
