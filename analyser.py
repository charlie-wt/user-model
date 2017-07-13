import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import ranker as rk
import decider as dc
import page as pg
import printer as pt
import record as rc

##### analyser ###############
# various functions to analyse a set of readings of a story.
##############################

def get_path_distribution ( page, ppr, prnt=False ):
# return dictionary of page : proportion of times it was picked from given page.
    options = {}

    for r in ppr:
        if page not in ppr[r]: continue
        idx = ppr[r].index(page)
        if idx == len(ppr[r]) - 1:
            options[0] = options[0] + 1 if 0 in options else 1
        else:
            next_page = ppr[r][idx+1]
            options[next_page] = options[next_page] + 1 if next_page in options else 1

    # normalise
    factor = 1 / sum(options.values())
    for o in options:
        options[o] = options[o] * factor

    if prnt: pt.print_options(options, page)
    return options

def pick_most_likely ( options ):
# for a dictionary of page : likelihood, return the page with the highest.
    if len(options) == 0: return None

    best = None
    for o in options:
        if best is None or options[o] > options[best]:
            best = o
    return best

def walk ( story, reading, user, paths_per_reading, max_steps=15, prnt=False, start_page=None ):
# walk through a story, based on the most popular user choices.
#   note: choosing a start_page that's not actually a starting page of the story
#         may break variable/condition stuff
    # set things up, choose a starting page
    visible = pg.update_all(story.pages, story, reading, user)
    if prnt:
        print("visible:")
        for p in visible:
            print("\t"+p.name)
    move_to_idx = dc.best(visible, rk.dist(user, story, user.path, visible))
    if start_page is not None:
        for p in visible:
            if p.name == start_page: move_to_idx = visible.index(p)
    visible = user.move(move_to_idx, visible, story, reading)
    if prnt: print("\nStart on", user.page().name, "\n\n=== start walk ===\n")

    path = []
    # traverse
    for i in range(0, max_steps):
        # get list of pages to visit from logs, eliminate the unreachable
        if prnt: print("---")
        prev_page = user.page()
        options = get_path_distribution(user.page(), paths_per_reading)
        quit = options[0] if 0 in options else None
        if prnt: pt.print_walk_full_options(visible, options)

        to_delete = [ k for k, v in options.items() if k not in visible ]
        for k in to_delete: del options[k]

        if prnt:
            print("\nfinal options:")
            for o in options:
                print("\t"+o.name)

        rc.add(path, prev_page, options, visible)

        # TODO - need to copy options into path if I want to do it like this:
        #        currently am putting reference to options in path, meaning
        #        adding quit to path re-adds quit to options: bad.
#        if quit is not None: path[-1].options[0] = quit

        # pick one of the remaining pages and move to it
        move_to = pick_most_likely(options)
        visible = user.move(visible.index(move_to), visible, story, reading)
        if prnt: print("\n[[ Chose", user.page().name, "]]")

        # stop if end reached
        if pg.last(user.page()):
            if prnt: print("\n=== end walk ===")
            rc.add(path, user.page(), {})
            return path
    if prnt: print("... max steps exceeded ...")
    return path
