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

def get_path_distribution_discourage_loops ( page, ppr, path, prnt=False ):
# return dictionary of page : proportion of times it was picked from given page.
# TODO - bit of a hack to stop the analysis walk from looping around the same
#        page forever (to see this, try 'The Titanic Criminal In Southampton',
#        but replace the call to this function in walk with one to
#        one to get_path_distribution).
    options = {}

    for r in ppr:
        if page not in ppr[r]: continue
        idx = ppr[r].index(page)
        if idx == len(ppr[r]) - 1:
            options[0] = options[0] + 1 if 0 in options else 1
        else:
            next_page = ppr[r][idx+1]
            options[next_page] = options[next_page] + 1 if next_page in options else 1

    # discourage revisiting nodes
    for p in options:
        if type(p) == int: continue
        options[p] = options[p] * (0.5)**ls.count(path, p.id)

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
    if len(paths_per_reading) == 0:
        print("can't walk", story.name+"; no logged readings.")
        return

    # set things up, choose a starting page
    visible = pg.update_all(story.pages, story, reading, user)

    firsts = {}
    for r in paths_per_reading:
        if len(paths_per_reading[r]) == 0: continue
        if paths_per_reading[r][0] not in firsts:
            firsts[paths_per_reading[r][0]] = 1
        else:
            firsts[paths_per_reading[r][0]] += 1
    first = max(firsts, key = lambda p : firsts[p])
    move_to_idx = ls.index(visible, first.id)
    visible = user.move(move_to_idx, visible, story, reading)

    if prnt: print("\nStart on", user.page().name,
                   "("+str(firsts[first]), "votes)",
                   "\n\n=== start walk ===\n")

    path = []
    # traverse
    for i in range(0, max_steps-1):
        # get list of pages to visit from logs, eliminate the unreachable
        if prnt: print("---")
#        options = get_path_distribution(user.page(), paths_per_reading)
        options = get_path_distribution_discourage_loops(user.page(), paths_per_reading, user.path)
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

def compare_paths ( story, store1, store2, prnt=False ):
# compare two paths taken through a story.
# TODO - don't just take into account the final path - also probabilities along
#        the way.
    path1 = [-1] + [ ls.index(story.pages, p.page.id) for p in store1[1:] if type(p) != int ]
    path2 = [-1] + [ ls.index(story.pages, p.page.id) for p in store2 if type(p) != int ]

    difference = levenshtein(path1, path2)

    if prnt: print("path edit difference:", difference)
    return difference

def path_similarity ( story, store1, store2, prnt=False ):
# get the proportional similarity between two paths
    #minimum = abs(len(store1) - len(store2))
    minimum = 0
    maximum = max(len(store1), len(store2))
    possible_range = maximum - minimum
    dist = compare_paths(story, store1, store2)

    similarity = 1 - (dist-minimum)/possible_range if possible_range != 0 else 1

    if prnt: print("similarity of paths:", pt.pc(similarity))
    return similarity

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

def levenshtein_similarity ( s1, s2, prnt=False ):
# get proportional similarity between two strings
    minimum = 0
    maximum = max(len(s1), len(s2))
    possible_range = maximum - minimum
    dist = levenshtein(s1, s2)

    similarity = 1 - (dist-minimum)/possible_range if possible_range != 0 else 1

    if prnt: print("similarity of", str(s1), "and", str(s2)+":", pt.pc(similarity))
    return similarity

def page_visits ( story, store, prnt=False ):
# get the number of times each page in the story was visited
    visits = []
    path = [ p.page for p in store if p.page != None ]

    for p in story.pages:
        visits.append((p, ls.count(path, p.id)))

    if prnt:
        print("number of visits per page:")
        for v in visits:
            print(v[1], ":", v[0].name)

    return visits
