import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page
import printer as pt
import record as rc
import reading as rd
import user as us
import ranker as rk
import decider as dc

##### traverser ##############
# for simulating a user moving through a story.
##############################

def traverse ( story, ranker, decider, max_steps=50, reading=None, user=None, prnt=False ):
# simulate a user walking through a story, making decisions. return a list of
# records (pages taken, and probabilities of each option at each page)
    if reading is None: reading = rd.Reading("reading-0", story)
    if user is None: user = us.User("user-0")

    visible = page.update_all(story.pages, story, reading, user)

    path = []
    # move to a page
    if prnt: print("traversing "+story.name+":")
    for i in range(max_steps):
        # move to a new page
        options = ranker(user, story, user.path, visible)

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

def traverse_many ( story, n=25, ranker=rk.rand, decider=dc.rand, max_steps=50 ):
# walk through a story n times, and return a list of stores
    reading = rd.Reading("reading-0", story)
    user = us.User("user-0")
    stores = []

    for i in range(n):
        stores.append(traverse(story, ranker, decider, max_steps, reading, user))
        reset(story, reading, user)

    return stores

def reset ( story, reading, user ):
    user.__init__(user.id)
    reading.__init__(reading.id, story)
