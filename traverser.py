import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import page
import location as lc

def traverse ( story, reading, user, fn, num_steps=10, prnt=False, visible=[] ):
    # see which pages are visible
    visible = page.update_all(story.pages, story, reading, user)

    # move to a page
    if prnt: print("traversing "+story.name+":")
    for i in range(0, num_steps):
        # move to a new page
        move_to_idx = fn(user, story, visible)
        #move_to_idx = dc.dist(user, story, visible)
        visible = user.move(move_to_idx, visible, story, reading)

        # print stuff
        if prnt: print("user is now at page '"+user.page().name+"', and is at location ("+str(user.lat())+", "+str(user.lon())+").")
        if prnt: print("\tvisible pages:")
        if prnt: print_visible(visible, story, user)

        # stop if you can't go anywhere
        if len(visible) == 0: break
        if prnt: print()

def print_visible ( vis, story, us ):
# print the list of visible pages
    for p in vis:
        page_loc = p.getLoc(story)
        if page_loc is not None:
            dist = lc.Location.metres(us.lat(), us.lon(), page_loc[0], page_loc[1])
            print("\t", p.name + "\t:\t" + p.id + " -> " + str(dist) + " metres away.")
        else:
            print("\t", p.name + "\t:\t" + p.id + ", which can be accessed from anywhere.")
