import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page as pg
import printer as pt
import record as rc
import reading as rd
import user as us
import ranker as rk
import decider as dc
import ls
import cache as ch

'''
traverser

for simulating a user moving through a story.
'''

def traverse ( story, ranker=rk.rand, decider=dc.rand, n=1, cache=None,
                    max_steps=50, prnt=False ):
    ''' simulate a user walking through a story n times, making decisions.
    return n lists of records (pages taken and probabilities of each option
    from that page).
    '''
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    stores = []
    if cache is None: cache = ch.Cache()

    for i in range(n):
        visible = pg.update_all(story.pages, story, reading, user)

        # put user in the middle at the start?
        locs = (0, 0)
        count = 0
        for p in visible:
            loc = p.get_loc(story)
            if loc:
                locs = (locs[0]+loc[0], locs[1]+loc[1])
                count += 1
        if count != 0:
            locs = (locs[0]/count, locs[1]/count)
            user.loc = locs

        path = []
        if prnt: print('traversing', story.name+':')
        # move to a page
        for i in range(max_steps):
            # record options, move to a new page
            options = ranker(user, story, visible, cache)
            rc.add(path, (user.page() if path else None), options, visible)
            visible = user.move(decider(visible, options), visible, story, reading)

            # stop if we can't go anywhere
            if pg.last(user.page(), visible):
                rc.add(path, user.page(), {})
                if prnt and n == 1:
                    pt.print_user_state(user)
                    print('=== end walk ===')
                break

            # print stuff
            if prnt and n == 1:
                pt.print_user_state(user)
                pt.print_visible(visible, story, user)
                print()
        stores.append(path)
        reset(story, reading, user)

    return stores if len(stores) > 1 else stores[0]

def reset ( story, reading, user ):
    ''' for using the same user/reading in multiple traversals. '''
    user.__init__(user.id)
    reading.__init__(reading.id, story)

def traverse_log ( story, paths_per_reading, max_steps=50, allow_quitting=False,
                   prnt=False):
    ''' traverse a story based on the most popular user choices. '''
    if len(paths_per_reading) == 0:
        raise ValueError("can't walk "+story.name+"; no logged readings.")
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")

    # setup
    visible = pg.update_all(story.pages, story, reading, user)
    # choose most popular starting page
    firsts = {}
    for r in paths_per_reading:
        if len(paths_per_reading[r]) == 0: continue
        if paths_per_reading[r][0] not in firsts:
            firsts[paths_per_reading[r][0]] = 1
        else:
            firsts[paths_per_reading[r][0]] += 1

    # turn scores for each page into proportions (probability) and put in store
    total = sum(firsts.values())
    for p in firsts:
        firsts[p] = firsts[p] / total
    first = max(firsts, key = lambda p : firsts[p])
    path = []
    rc.add(path, None, firsts, visible)

    # move to first page
    move_to_idx = ls.index(visible, first.id)
    visible = user.move(move_to_idx, visible, story, reading)

    if prnt: print("\nStart on", user.page().name,
                   "("+pt.pc(firsts[first])+")",
                   "\n\n=== start walk ===\n")

    # traverse
    for i in range(max_steps-1):
        # get list of pages to visit from logs
        if prnt: print("---")
#        options = get_path_distribution(user.page(), paths_per_reading)
        options = get_path_distribution_discourage_loops(
                user.page(), paths_per_reading, user.path)
        quit = options[0] if 0 in options else 0
        if prnt: pt.print_walk_full_options(visible, options, allow_quitting)

        # eliminate unreachable pages, add back visible but never visited ones.
        to_delete = [ k for k, v in options.items() if k not in visible ]
        for k in to_delete: del options[k]
        rc.fill_options(options, visible)
        if allow_quitting:
            options[0] = quit

        if prnt:
            print("\nfinal options:")
            for o in options:
                print("\t" + (o.name if o != 0 else '--Quit--'))

        rc.add(path, user.page(), options, visible)

        # pick one of the remaining pages and move to it
        move_to = pick_most_likely(options)
        if move_to == 0:
            if prnt:
                print("\n[[ Chose to quit ]]")
                print("\n=== end walk ===")
            rc.add(path, user.page(), {})
            return path
        visible = user.move(visible.index(move_to), visible, story, reading)
        if prnt: print("\n[[ Chose", user.page().name, "]]")

        path[-1].options[0] = quit

        # stop if end reached
        if pg.last(user.page(), visible):
            if prnt: print("\n=== end walk ===")
            rc.add(path, user.page(), {})
            return path
    if prnt: print("... max steps exceeded ...")
    return path

def get_path_distribution ( page, ppr, prnt=False ):
    ''' return dictionary of page : proportion of times it was picked from
    given page.
    '''
    options = {}

    # count up visits to each page from [page] for each reading.
    for r in ppr:
        if page not in ppr[r]: continue
        idx = ppr[r].index(page)
        if idx == len(ppr[r]) - 1:
            # the option of quitting the story
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
    ''' return dictionary of page : proportion of times it was picked from
    given page.
    '''
    # TODO - bit of a hack to stop the log traversal from looping around the
    #        same page forever (to see this, try 'The Titanic Criminal In
    #        Southampton', but replace the call to this function in
    #        traverse_log() with a call to get_path_distribution).
    options = {}

    # count up visits to each page from [page] for each reading.
    for r in ppr:
        if page not in ppr[r]: continue
        idx = ppr[r].index(page)
        if idx == len(ppr[r]) - 1:
            # the option of quitting the story
            options[0] = options[0] + 1 if 0 in options else 1
        else:
            next_page = ppr[r][idx+1]
            options[next_page] = options[next_page] + 1 if next_page in options else 1

    # discourage revisiting nodes
    factor = 0.2
    for p in options:
        if type(p) == int: continue
        options[p] = options[p] * factor**ls.count(path, p.id)

    # normalise
    if sum(options.values()) != 0:
        factor = 1 / sum(options.values())
        for o in options:
            options[o] = options[o] * factor

    if prnt: pt.print_options(options, page)
    return options

def pick_most_likely ( options ):
    ''' for a dictionary of page : likelihood, return the page with the
    highest.
    '''
    if len(options) == 0: return None
    return max(options, key = lambda o : options[o])
