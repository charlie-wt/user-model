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

num_steps = 35



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

    to_delete = [ k for k, v in options.items() if k not in visible ]

    # TODO - for some reason if I get rid of these print statements it break
    print("\nHave to delete:")
    for k in to_delete:
        print(k.name) if type(k) != int else print("--End--")

    for k in to_delete: del options[k]

    move_to = an.pick_most_likely(options)
    visible = user.move(visible.index(move_to), visible, sto, reading)
    page = move_to

    if pg.last(page):
        print("finished at page", page.name)
        break

    print("\nNow at", page.name)
