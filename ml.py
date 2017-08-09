import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page as pg
import user as us
import reading as rd
import heuristics as hs
import ls

##### ml #####################
# machine learning stuff.
##############################

def formalise ( story, path, cache=None, prnt=False, exclude_poi=False ):
# put list of pages (forming a path) into a form that can be interpreted by ml.
# TODO - better name, make sure it works right with the (eventual) actual ml
#        stuff.
# TODO - in some way normalise data -> the same page could be either chosen or
#        not chosen based on what the other options at the time are.
#           - probably just lerp between min & max values with each option set?
    xs = []
    ys = []

    # create stuff
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    if cache is None: cache = ls.auto_dict()
    visible = pg.update_all(story.pages, story, reading, user)

    # perform reading
    for i in range(0, len(path)-1):
        # calculate heuristics for each option, and add to the list
        if len(visible) > 1:
            for p in visible:
                walk_dist = hs.walk_dist(p, user, story, cache)
                visits = hs.visits(p, user)
                alt = hs.altitude(p, user, story, cache)
                if not exclude_poi: poi = hs.points_of_interest(p, user, story, cache)
                mention = hs.mentioned(p, user, story, cache)

                if not exclude_poi:
                    xs.append((walk_dist, visits, alt, poi, mention))
                else:
                    xs.append((walk_dist, visits, alt, mention))
                ys.append((1 if p == path[i] else 0))

        # move to next page
        move_to_idx = ls.index(visible, path[i].id)
        visible = user.move(move_to_idx, visible, story, reading)

    if len(ys) == 0:
        raise ValueError('Story supplied to formalise contains no choices.')

    if prnt:
        print('formalised path data:')
        for (x, y) in zip(xs, ys):
            print(y, "<-", x)

    return (xs, ys)

def logreg ( story, path, cache=None, prnt=False ):
    raise NotImplementedError('lol')

def nn ( story, path, cache=None, prnt=False ):
    raise NotImplementedError('lol')
