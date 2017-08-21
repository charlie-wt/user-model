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

def traverse ( story, ranker, decider, max_steps=50, reading=None, user=None,
               cache=None, prnt=False ):
# simulate a user walking through a story, making decisions. return a list of
# records (pages taken, and probabilities of each option at each page)
    if reading is None: reading = rd.Reading("reading-0", story)
    if user is None: user = us.User("user-0")
    if cache is None: cache = ls.auto_dict()

    visible = page.update_all(story.pages, story, reading, user)

    path = []
    # move to a page
    if prnt: print("traversing "+story.name+":")
    for i in range(max_steps):
        # record options, move to new page
        options = ranker(user, story, visible, cache)
        rc.add(path, (user.page() if path else None), options, visible)
        visible = user.move(decider(visible, options), visible, story, reading)

        # print stuff
        if prnt:
            pt.print_user_state(user)
            pt.print_visible(visible, story, user)

        # stop if we can't go anywhere
        if page.last(user.page(), visible):
            rc.add(path, user.page(), {})
            break

        if prnt: print()
    return path

def traverse_many ( story, n=100, ranker=rk.rand, decider=dc.rand, cache=None,
                    max_steps=50 ):
# walk through a story n times, and return a list of stores
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    stores = []
    if cache is None: cache = ls.auto_dict()

    for i in range(n):
        visible = page.update_all(story.pages, story, reading, user)

        path = []
        # move to a page
        for i in range(max_steps):
            # record options, move to a new page
            options = ranker(user, story, visible, cache)
            rc.add(path, (user.page() if path else None), options, visible)
            visible = user.move(decider(visible, options), visible, story, reading)

            # stop if we can't go anywhere
            if page.last(user.page(), visible):
                rc.add(path, user.page(), {})
                break
        stores.append(path)
        reset(story, reading, user)

    return stores

def reset ( story, reading, user ):
# for using the same user/reading in multiple traversals
    user.__init__(user.id)
    reading.__init__(reading.id, story)
