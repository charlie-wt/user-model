import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page
import printer as pt
import record as rc

##### traverser ##############
# for simulating a user moving through a story.
##############################

def traverse ( story, reading, user, ranker, decider, max_steps=10, prnt=False, visible=[] ):
    visible = page.update_all(story.pages, story, reading, user)

    path = []
    # move to a page
    if prnt: print("traversing "+story.name+":")
    for i in range(0, max_steps):
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

def reset ( story, reading, user ):
    user.__init__(user.id)
    reading.__init__(reading.id, story)
