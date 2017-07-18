import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import ranker as rk
import decider as dc
import page as pg
import printer as pt
import record as rc
import ls

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
    if sum(options.values()) != 0:
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
    for i in range(0, max_steps-1):
        # get list of pages to visit from logs, eliminate the unreachable
        if prnt: print("---")
        options = get_path_distribution(user.page(), paths_per_reading)
        quit = options[0] if 0 in options else 0
        if prnt: pt.print_walk_full_options(visible, options)

        to_delete = [ k for k, v in options.items() if k not in visible ]
        for k in to_delete: del options[k]

        if prnt:
            print("\nfinal options:")
            for o in options:
                print("\t"+o.name)

        rc.add(path, user.page(), options, visible)

        # pick one of the remaining pages and move to it
        move_to = pick_most_likely(options)
        visible = user.move(visible.index(move_to), visible, story, reading)
        if prnt: print("\n[[ Chose", user.page().name, "]]")

        path[-1].options[0] = quit

        # stop if end reached
        if pg.last(user.page()):
            if prnt: print("\n=== end walk ===")
            rc.add(path, user.page(), {})
            return path
    if prnt: print("... max steps exceeded ...")
    return path

def compare_paths ( story, store1, store2 ):
# compare two paths taken through a story.
# TODO - don't just take into account the final path - also probabilities along
#        the way.
    path1 = [-1] + [ ls.index(story.pages, p.page.id) for p in store1[1:] if type(p) != int ]
    path2 = [-1] + [ ls.index(story.pages, p.page.id) for p in store2 if type(p) != int ]
    
    return levenshtein(path1, path2)

def path_similarity ( story, store1, store2 ):
# get the proportional similarity between two paths
    #minimum = abs(len(store1) - len(store2))
    minimum = 0
    maximum = max(len(store1), len(store2))
    possible_range = maximum - minimum
    dist = compare_paths(story, store1, store2)
    return 1 - (dist-minimum)/possible_range if possible_range != 0 else 1

def levenshtein ( s1, s2 ):
# get the edit distance between two strings
# based off implementation @ https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_two_matrix_rows

    # v0: row above the current row in the matrix.
    #     initialise to top row; row where s1 = ""
    v0 = list(range(0, len(s2)+1))
    # v1: current row being calculated.
    v1 = [0] * (len(s2)+1)

    # fill v1, as distance from v0
    for i in range(0, len(s1)):
        v1[0] = i + 1

        for j in range(0, len(s2)):
            # substitution cost (0 if chars are the same -> no substitution)
            cost = 0 if s1[i] == s2[j] else 1

            v1[j+1] = min(v1[j] + 1,    # deletion
                          v0[j+1] + 1,  # insertion
                          v0[j] + cost) # substitution

        # current row -> previous row for next iteration
        v0 = v1[:]

    # bottom right of matrix = total dist
    return v0[-1]

def levenshtein_similarity ( s1, s2 ):
# get proportional similarity between two strings
    minimum = 0
    maximum = max(len(s1), len(s2))
    possible_range = maximum - minimum
    dist = levenshtein(s1, s2)
    return 1 - (dist-minimum)/possible_range if possible_range != 0 else 1
