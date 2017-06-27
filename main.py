import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import time

import importer as imp
import ls
import reading as rd
import user as us
import decider as dc
import page



story_name = "The Titanic Criminal In Southampton"

num_steps = 15



def print_visible ( vis, story, us ):
# print the list of visible pages
    for p in vis:
        page_loc = p.getLoc(story)
        if page_loc is not None:
            dist = imp.location.Location.metres(us.lat(), us.lon(), page_loc[0], page_loc[1])
            print("\t", p.name + "\t:\t" + p.id + " -> " + str(dist) + " metres away.")
        else:
            print("\t", p.name + "\t:\t" + p.id + ", which can be accessed from anywhere.")

# create story, reading & user
sto = imp.storyFromJSON(story_name, [False, False, False, False, True ])
reading = rd.Reading("reading-0", sto, "inprogress", time.time())
user = us.User("user-0")
print("There are", len(reading.vars), "variables in the story.\n")

# see which pages are visible
visible = page.update_all(sto.pages, sto, reading, user)

# move to a page
print("\n.MOVEMENT.")
for i in range(0, num_steps):
    # move to a new page
    move_to_idx = dc.rand(user, sto, visible)
#    move_to_idx = dc.dist(user, sto, visible)
    visible = user.move(move_to_idx, visible, sto, reading)

    # print stuff
    print("user is now at page '" + user.page().name + "', and is at location (" + str(user.lat()) + ", " + str(user.lon()) + ").")
    print("\tvisible pages:")
    print_visible(visible, sto, user)

    # stop if you can't go anywhere
    if len(visible) == 0: break
    print("\n")
