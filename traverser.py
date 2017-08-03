import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page
import printer as pt
import record as rc
import reading as rd
import user as us
import ranker as rk
import decider as dc
import ls

##### traverser ##############
# for simulating a user moving through a story.
##############################

def traverse ( story, ranker, decider, max_steps=50, reading=None, user=None, cache=None, prnt=False ):
# simulate a user walking through a story, making decisions. return a list of
# records (pages taken, and probabilities of each option at each page)
    if reading is None: reading = rd.Reading("reading-0", story)
    if user is None: user = us.User("user-0")
    if cache is None: cache = ls.nested_dict()

    visible = page.update_all(story.pages, story, reading, user)

    path = []
    # move to a page
    if prnt: print("traversing "+story.name+":")
    for i in range(max_steps):
        # optionally start the user at a location in the middle of the start pages.
        moved = False
        for p in user.path:
            if p.getLoc(story) is not None:
                moved = True
                break
        if not moved:
            locs = [ p.getLoc(story) for p in visible if p.getLoc(story) is not None ]
            lats = [ loc[0] for loc in locs ]
            lons = [ loc[1] for loc in locs ]
            if len(locs) > 0: user.loc = ((sum(lats)/len(lats)), (sum(lons)/len(lons)))

        # move to a new page
        options = ranker(user, story, user.path, visible, cache)

        rc.add(path, (user.page() if path else None), options, visible)

        move_to_idx = decider(visible, options)
        visible = user.move(move_to_idx, visible, story, reading)

        # print stuff
        if prnt:
            pt.print_user_state(user)
            pt.print_visible(visible, story, user)

        # stop if you can't go anywhere
        if page.last(user.page(), visible):
            rc.add(path, user.page(), {})
            break

        if prnt: print()
    return path

def traverse_many ( story, n=25, ranker=rk.rand, decider=dc.rand, cache=None, max_steps=50 ):
# walk through a story n times, and return a list of stores
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    stores = []
    if cache is None: cache = ls.nested_dict()

    for i in range(n):
        visible = page.update_all(story.pages, story, reading, user)

        path = []
        # move to a page
        for i in range(max_steps):
            # optionally start the user at a location in the middle of the start pages.
            moved = False
            for p in user.path:
                if p.getLoc(story) is not None:
                    moved = True
                    break
            if not moved:
                locs = [ p.getLoc(story) for p in visible if p.getLoc(story) is not None ]
                lats = [ loc[0] for loc in locs ]
                lons = [ loc[1] for loc in locs ]
                if len(locs) > 0: user.loc = ((sum(lats)/len(lats)), (sum(lons)/len(lons)))

            # move to a new page
            options = ranker(user, story, user.path, visible, cache)

            rc.add(path, (user.page() if path else None), options, visible)

            move_to_idx = decider(visible, options)
            visible = user.move(move_to_idx, visible, story, reading)

            # stop if you can't go anywhere
            if page.last(user.page(), visible):
                rc.add(path, user.page(), {})
                break
        stores.append(path)
        reset(story, reading, user)

    return stores

def step_predict ( story, log_store, ranker, prnt=False ):
# compare the proportions of user visits from a log-based reading with the
# proportional probabilities spat out by the ranker, for n steps ahead.
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    visible = page.update_all(story.pages, story, reading, user)
    error = 0
    num_options = 0

    # perform first step
    options = ranker(user, story, user.path, visible)
    for o in options:
        error += abs(log_store[0].options[o] - options[o])#**2
    num_options += len(options)
    move_to_idx = ls.index(visible, log_store[1].page.id)
    visible = user.move(move_to_idx, visible, story, reading)

    # perform remaining steps in reading
    for i in range(1, len(log_store)-1):
        # perform movement
        options = ranker(user, story, user.path, visible)

        log_options = {}
        for p in log_store[i].options:
            if p != 0: log_options[p] = log_store[i].options[p]

        # compare options presented by ranker with popularity of options in logs
        for o in options:
            if type(o) is not page.Page: continue
            error += abs(log_options[o] - options[o])#**2
        num_options += len(options)

        # move to next page
        move_to_idx = ls.index(visible, log_store[i+1].page.id)
        visible = user.move(move_to_idx, visible, story, reading)

    if prnt: print("error for step-ahead prediction of", story.name+":",
                   pt.pc(error / num_options, 2))
    return error / num_options

def reset ( story, reading, user ):
    user.__init__(user.id)
    reading.__init__(reading.id, story)
