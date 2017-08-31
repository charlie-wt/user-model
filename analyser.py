import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

from datetime import timedelta

import ranker as rk
import decider as dc
import page as pg
import printer as pt
import record as rc
import ls
import cache as ch
import reading as rd
import user as us
import traverser as tr
import location as lc
import heuristics as hs

'''
analyser

various functions to analyse a set of readings of a story.
'''

def compare_paths ( story, store1, store2, prnt=False ):
    ''' compare two paths taken through a story. '''
# TODO - don't just take into account the final path - also probabilities along
#        the way.
    # convert paths to lists
    path1 = [-1] + [ p.page for p in store1[1:] if type(p) != int ]
    path2 = [-1] + [ p.page for p in store2[1:] if type(p) != int ]

    difference = levenshtein(path1, path2)

    if prnt: print("path edit difference:", difference)
    return difference

def path_similarity ( story, store1, store2, prnt=False ):
    ''' get the proportional similarity between two paths. '''
    minimum = 0
    maximum = max(len(store1), len(store2))
    possible_range = maximum - minimum
    dist = compare_paths(story, store1, store2)

    similarity = 1 - (dist-minimum)/possible_range if possible_range != 0 else 1

    if prnt: print("similarity of paths:", pt.pc(similarity))
    return similarity

def levenshtein ( s1, s2 ):
    ''' get the edit distance between two strings.
    based off implementation @ https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_two_matrix_rows
    '''

    # v0: row above the current row in the matrix.
    #     initialise to top row; row where s1 = ""
    v0 = list(range(len(s2)+1))
    # v1: current row being calculated.
    v1 = [0] * (len(s2)+1)

    # fill v1, as distance from v0
    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
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
    ''' get proportional similarity between two strings. '''
    minimum = 0
    maximum = max(len(s1), len(s2))
    possible_range = maximum - minimum
    dist = levenshtein(s1, s2)

    similarity = 1 - (dist-minimum)/possible_range if possible_range != 0 else 1

    if prnt: print("similarity of", str(s1), "and", str(s2)+":", pt.pc(similarity))
    return similarity

def page_visits ( story, stores, prnt=False ):
    ''' find out how many times each page was visited for 1-n readings. '''
    if type(stores[0]) is not list: stores = [stores]
    total_visits = {}
    for p in story.pages: total_visits[p] = 0
    for s in stores:
        path = [ p.page for p in s if p.page != None ]
        for p in story.pages:
            if p not in total_visits: print("no")
            total_visits[p] += ls.count(path, p.id)

    if prnt:
        print("number of visits per page of", story.name, "("+ \
              str(len(stores)), "reading"+("s.)" if len(stores)>1 else ".)"))
        for v in total_visits:
            print(total_visits[v], ":", v.name)

    return total_visits

def most_visited ( story, stores, prnt=False ):
    ''' get a list of pages & the proportion of times they were visited, ordered
    as tuples.
    '''
    visits = page_visits(story, stores)

    # get proportions
    proportions = []
    for p in visits:
        proportions.append((p, visits[p]/len(stores)))
    proportions.sort(key = lambda p : -p[1])

    if prnt:
        print("proportions of visits to pages of", story.name, "per reading")
        for p in proportions:
            print(pt.pc(p[1]), p[0].name)
        print()

    return proportions

def log_most_visited ( story, ppr, prnt=False ):
    ''' similar to most_visited, but take in a 'paths per reading' list from a
    log.
    '''
    # count up the number of visits per page
    visits = {}
    for p in story.pages: visits[p] = 0
    for r in ppr:
        for p in story.pages:
            visits[p] += ls.count(ppr[r], p.id)

    # turn number of visits into proportions per reading, then sort descending.
    proportions = []
    for p in visits:
        proportions.append((p, visits[p]/len(ppr)))
    proportions.sort(key = lambda p : -p[1])

    if prnt:
        print("proportions of visits to pages of", story.name, "per reading")
        for p in proportions:
            print(pt.pc(p[1]), p[0].name)
        print()

    return proportions

def get_unreachables ( story, stores=None, cache=None, prnt=False ):
    ''' for a bunch of readings, return the pages that were never reached. '''
    if stores is None: stores = tr.traverse(story, n=150, cache=cache)
    visits = page_visits(story, stores)
    unreachables = [ p for p in visits if visits[p] == 0 ]

    if prnt:
        if len(unreachables) == 0:
            print("all the pages in", story.name, "can be reached!")
        else:
            print("unreached pages in", story.name+":")
            pt.print_pages(unreachables, print_id=True)

    return unreachables

def distance_travelled ( story, stores, prnt=False ):
    ''' total distance travelled while walking the given route of the story. '''
    if type(stores[0]) is not list: stores = [stores]
    distances = []

    for store in stores:
        distance = 0

        # get the location of the first location-locked page
        startidx = 0
        curr_loc = (0, 0)
        for i in range(len(store)):
            if store[i].page is not None and \
               store[i].page.get_loc(story) is not None:
                curr_loc = store[i].page.get_loc(story)
                startidx = i+1
                break
        # measure the distance to each page from there
        for i in range(startidx, len(store)):
            dest = store[i].page
            if dest is None: continue
            dest_loc = dest.get_loc(story)
            if dest_loc is None: continue

            distance += lc.metres(curr_loc, dest_loc)
            curr_loc = dest_loc

        distances.append(distance)

    if prnt:
        if len(stores) == 1:
            print("travelled", distance, "metres while reading", story.name)
        else:
            print("average distance for", len(distances), "readings:",
                  str(int(sum(distances)/len(distances)))+"m")

    return distances

def branching_factor ( story, stores, prnt=False ):
    ''' get the average number of choices from any given page. '''
    total = 0

    for s in stores:
        options = [ len(r.options) for r in s ]
        total += sum(options)/len(s)
    bf = total / len(stores)

    if prnt: print("average branching factor for", story.name+":", bf)
    return bf

def filter_readings ( story, epr, max_metres_per_second=5, legacy=False,
                      demo_mode=False, prnt=False ):
    ''' take an events per reading dictionary, and filter out illegitimate
    ones.
    '''
    filtered = {}
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    dev_ids = [
        "5757f7c29000c74f10000003",
        "575acfcc376d4e2f4200000a",
        "576c37ced601c536700000cc",
        "576e5acbd601c53670000386",
        "575e8c8f61c930d542000022",
        "5764008ea0672b6e5b000003",
        "576afdaed601c5367000005d",
        "576fdc04d601c53670000804",
        "57f50d9fc7dde2221000031a",
        "5757f7c29000c74f10000003"
    ]

    for reading_id in epr:
        removed = False

        # 1 : if reading was done by a dev
        if not demo_mode:
            user_id = epr[reading_id][0].user
            if user_id in dev_ids:
                removed = True
                if prnt: print("removing", reading_id+": user has dev id")

            if removed: continue

        # 2 : if the reading is empty
        pages = pg.from_log_events(story, epr[reading_id], legacy)
        if len(pages) == 0:
            removed = True
            if prnt: print("removing", reading_id+": empty reading")

        if removed: continue

        # 3 : if the path taken was impossible
        visible = pg.update_all(story.pages, story, reading, user)
        dist = 0
        curr_loc = (0, 0)
        for p in pages:
            if p.get_loc(story) is not None:
                curr_loc = p.get_loc(story)

        for p in pages:
            if p not in visible:
                removed = True
                if prnt: print("removing", reading_id+": impossible reading")
                break

        #     (also count up the total distance travelled here.)
            dest_loc = p.get_loc(story)
            if dest_loc is not None:
                dist += lc.metres(curr_loc, dest_loc)
                curr_loc = dest_loc

            visible = user.move(visible.index(p), visible, story, reading)
        tr.reset(story, reading, user)

        if removed: continue

        # 4 : if user travelled at a speed greater than max_metres_per_second
        av_dist = dist / len(pages)
        av_duration = (epr[reading_id][-1].date - epr[reading_id][0].date) / len(pages)
        if demo_mode:
            bad_speed = av_duration.total_seconds() > av_dist / max_metres_per_second
        else:
            bad_speed = av_duration.total_seconds() < av_dist / max_metres_per_second
        if bad_speed:
            removed = True
            if prnt:
                if av_duration.total_seconds() > 0:
                    av_speed = av_dist / av_duration.total_seconds()
                    fast_or_slow = "slow" if demo_mode else "fast"
                    print("removing", reading_id+": moved too", fast_or_slow,
                          "(average speed was "+pt.fmt(av_speed,dec=1)+"m/s).")
                else:
                    print("removing", reading_id+": reading lasted 0 seconds.")
            continue

        if removed: continue

        # if we've made it this far, the reading's (probably) valid
        filtered[reading_id] = pages

    if prnt: print("found", len(filtered),
                   ("demo-mode" if demo_mode else "real"), "reading"+
                   ("s" if len(filtered) != 1 else ""), "for", story.name)
    return filtered

def measure_ranker ( story, ppr, ranker, cache=None, prnt=False ):
    ''' see how the ordering of a ranker measures up against the choices made in
    logs.
    '''
    if cache is None: cache = ch.Cache()
    # simple list to store the index of each choice, in chronological order.
    options_taken = []

    # fill list containing the ranking of each option taken
    # (0 -> 'best', according to ranker)
    for r in ppr.values():
        # create stuff
        reading = rd.Reading("reading-0", story)
        user = us.User("user-0")
        visible = pg.update_all(story.pages, story, reading, user)

        # perform reading
        for i in range(0, len(r)):
            # get ranker's preference (best -> worst)
            options = ranker(user, story, visible, cache)
            ranking = sorted(options.keys(), key = lambda p : -options[p])

            # record which of the ranker's options was chosen
            if len(ranking) > 1:
                options_taken.append(ranking.index(r[i]))

            # move to next page
            move_to_idx = ls.index(visible, r[i].id)
            visible = user.move(move_to_idx, visible, story, reading)
        tr.reset(story, reading, user)

    if len(options_taken) == 0:
        raise ValueError('Story supplied to measure_ranker contains no choices.')

    # create list that instead has index : count
    counts = [0] * (max(options_taken)+1)
    for o in options_taken:
        counts[o] += 1
    # smush counts to be out of 1 (ie. the proportion of total choices)
    for i in range(len(counts)):
        counts[i] /= len(options_taken)

    if prnt:
        print('log choices compared to ranker preference:')
        for i in range(len(counts)):
            print((' '+str(i) if i < 10 else i), ':', counts[i])

    return counts
