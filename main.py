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

num_steps = 35



# create story, reading & user
sto = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", sto)
user = us.User("user-0")

# traverse
#tr.traverse(sto, reading, user, rk.rand, dc.best, num_steps, True)
#print("--- done ---\n")
#pt.print_path(sto, user.path)

# load logs
paths_per_reading = imp.pathPagesFromJSON("old-logs", sto, True)
an.walk(sto, reading, user, paths_per_reading, 15, True)
