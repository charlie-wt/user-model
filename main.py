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
import ls



story_name = "Notes on an Illegible City"

num_steps = 15



# create story, reading & user
sto = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", sto)
user = us.User("user-0")

# traverse
sim_store = tr.traverse(sto, reading, user, rk.guess, dc.best, num_steps)
#print("--- done ---\n")
#pt.print_path(sto, user.path)
#pt.print_path(sto, user.path)
#for r in sim_store:
#    print("page:", (r.page.name if r.page is not None else "--Start--"))
#    for o in r.options:
#        print("\t"+pt.pc(r.options[o]), ":", (o.name if type(o) != int else "--Quit--"))
sim_path = user.path[:]
tr.reset(sto, reading, user)

# load logs
paths_per_reading = imp.pathPagesFromJSON("old-logs", sto)
log_store = an.walk(sto, reading, user, paths_per_reading, num_steps)
#pt.print_path(sto, user.path)
#for r in store:
#    print("page:", r.page.name)
#    for o in r.options:
#        print("\t"+pt.pc(r.options[o]), ":", (o.name if type(o) != int else "--Quit--"))
log_path = user.path[:]

pt.print_sim_log_comparison(sim_path, log_path)

print()
print("St Michael's Church:")
for r in log_store:
    if r.page.name == "St Michael's Church":
        print("log:")
        for o in r.options:
            print("\t"+pt.pc(r.options[o]), ":", (o.name if type(o) != int else "--Quit--"))
for r in sim_store:
    if r.page is not None and r.page.name == "St Michael's Church":
        print("sim:")
        for o in r.options:
            print("\t"+pt.pc(r.options[o]), ":", (o.name if type(o) != int else "--Quit--"))
