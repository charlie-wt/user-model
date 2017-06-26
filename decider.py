import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import location as l
import page

import ls
import math
import random

def dist ( user, story, pages ):
    mindist = float('inf')
    minidx = -1
    for page in pages:
        page_loc = page.getLoc(story)
        if page_loc == None: page_loc = user.loc
        d = l.Location.metres(user.lat(), user.lon(), page_loc[0], page_loc[1])
        if ( d < mindist ):
            mindist = d
            minidx = pages.index(page)
    return minidx

def rand ( user, story, pages ):
    return math.floor(random.random() * len(pages))
