import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page
import printer as pt

def traverse ( story, reading, user, ranker, decider, num_steps=10, prnt=False, visible=[] ):
    path = []
    visible = page.update_all(story.pages, story, reading, user)

    # move to a page
    if prnt: print("traversing "+story.name+":")
    for i in range(0, num_steps):
        # move to a new page
        move_to_idx = decider(visible, ranker(user, story, path, visible))
        visible = user.move(move_to_idx, visible, story, reading)
        path.append(user.page())

        # print stuff
        if prnt: print("user is now at page '"+user.page().name+"', and is at location ("+str(user.lat())+", "+str(user.lon())+").")
        if prnt: print("\tvisible pages:")
        if prnt: pt.print_visible(visible, story, user)

        # stop if you can't go anywhere
        if len(visible) == 0 or user.page().name == "Finish" or user.page() == "Finish Story": break
        if prnt: print()
    return path
