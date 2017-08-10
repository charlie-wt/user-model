import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import traverser as tr
import page as pg
import user as us
import reading as rd
import heuristics as hs
import ranker as rk
import ls

##### ml #####################
# machine learning stuff.
##############################

def formalise ( story, ppr, cache=None, prnt=False, exclude_poi=False ):
# put list of pages (forming a path) into a form that can be interpreted by ml.
# TODO - in some way normalise data -> the same page could be either chosen or
#        not chosen based on what the other options at the time are.
#           - probably just lerp between min & max values with each option set?
#           - but also would want to know if all pages are far away, since then
#             people might just quit.
#               - to that end, could supply *both* the absolute values and
#                 rankings based on those values. Would make things slower.
    if prnt: print('formalised path data:')
    xs = []
    ys = []

    # create stuff
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    if cache is None: cache = ls.auto_dict()

    # perform reading
    count = 1
    for r in ppr:
        path = ppr[r]
        visible = pg.update_all(story.pages, story, reading, user)
        for i in range(0, len(path)-1):
            # calculate heuristics (and rankings) for each option, and store
            if len(visible) > 1:
                # get rankings
                walk_dist_ranking = rk.walk_dist(user, story, visible, cache)
                visits_ranking = rk.visits(user, story, visible, cache)
                alt_ranking = rk.alt(user, story, visible, cache)
                poi_ranking = rk.poi(user, story, visible, cache)
                mention_ranking = rk.mentioned(user, story, visible, cache)

                for p in visible:
                    # get heuristic values for this page
                    walk_dist = hs.walk_dist(p, user, story, cache)
                    visits = hs.visits(p, user)
                    alt = hs.altitude(p, user, story, cache)
                    if not exclude_poi:
                        poi = hs.points_of_interest(p, user, story, cache)
                    mention = hs.mentioned(p, user, story, cache)

                    # get ranking for this page
                    r_dst = walk_dist_ranking[p]
                    r_vis = visits_ranking[p]
                    r_alt = alt_ranking[p]
                    if not exclude_poi:
                        r_poi = poi_ranking[p]
                    r_men = mention_ranking[p]

                    # add heuristics/values to input vector
                    if not exclude_poi:
                        xs.append((walk_dist, visits, alt, poi, mention,
                                   r_dst, r_vis, r_alt, r_poi, r_men))
                    else:
                        xs.append((walk_dist, visits, alt, mention,
                                   r_dst, r_vis, r_alt, r_men))
                    # add result (whether the page was chosen) to output vector
                    ys.append((1 if p == path[i] else 0))

                    if prnt: print(count, ':', ys[-1], '<-', xs[-1])
                    count += 1

            # move to next page
            move_to_idx = ls.index(visible, path[i].id)
            visible = user.move(move_to_idx, visible, story, reading)
        tr.reset(story, reading, user)

    if len(ys) == 0:
        raise ValueError('Story supplied to formalise contains no choices.')

#    if prnt:
#        print('formalised path data:')
#        for (x, y) in zip(xs, ys):
#            print(y, "<-", x)

    return (xs, ys)

def logreg ( story, path, cache=None, prnt=False ):
    raise NotImplementedError('lol')

def nn ( story, path, cache=None, prnt=False ):
    raise NotImplementedError('lol')
