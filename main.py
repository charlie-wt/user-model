import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import importer as imp
import reading as rd
import user as us
import ranker as rk
import decider as dc
import page
import traverser as tr
import printer as pt
import analyser as an



story_name = "Notes on an Illegible City"

num_steps = 15



# create story, reading & user
sto = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", sto)
user = us.User("user-0")

# traverse
path = tr.traverse(sto, reading, user, rk.guess, dc.best, num_steps)
print("--- done ---\n")
pt.print_path(sto, path)

# load logs
#ppr = imp.pathPagesFromJSON("old-logs", sto)
#print("Found", len(ppr), "readings for", sto.name+".")
#
# TODO - init stuff
#
#for i in range(0, 5):
#    options = an.get_path_distribution(page, ppr, True)
#    move_to = an.pick_most_likely(options)
#    if page == 0 or page == None: break
#    print("\nNow at", page.name)
