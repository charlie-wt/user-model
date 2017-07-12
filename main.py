import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import importer as imp
import reading as rd
import user as us
import ranker as rk
import decider as dc
import page as pg
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
#tr.traverse(sto, reading, user, rk.guess, dc.best, num_steps)
#print("--- done ---\n")
#pt.print_path(sto, user.path)

# load logs
paths_per_reading = imp.pathPagesFromJSON("old-logs", sto)
print("Found", len(paths_per_reading), "readings for", sto.name+".")

visible = pg.update_all(sto.pages, sto, reading, user)
move_to_idx = dc.best(visible, rk.dist(user, sto, user.path, visible))
page = sto.pages[move_to_idx]

for i in range(0, num_steps):
    options = an.get_path_distribution(page, paths_per_reading, True)
    move_to = an.pick_most_likely(options)
    user.path.append(move_to)
    page = move_to

    if pg.last(page): break

    print("\nNow at", page.name)
