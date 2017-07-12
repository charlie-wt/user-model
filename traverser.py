import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page
import printer as pt

##### traverser ##############
# for simulating a user moving through a story.
##############################

def traverse ( story, reading, user, ranker, decider, num_steps=10, prnt=False, visible=[] ):
    visible = page.update_all(story.pages, story, reading, user)

    # move to a page
    if prnt: print("traversing "+story.name+":")
    for i in range(0, num_steps):
        # move to a new page
        move_to_idx = decider(visible, ranker(user, story, user.path, visible))
        visible = user.move(move_to_idx, visible, story, reading)

        # print stuff
        if prnt:
            pt.print_user_state(user)
            pt.print_visible(visible, story, user)

        # stop if you can't go anywhere
        if page.last(user.page(), visible): break

        if prnt: print()
