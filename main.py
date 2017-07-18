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

max_steps = 15



# create/load stuff
story = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", story)
user = us.User("user-0")
paths_per_reading = imp.pathPagesFromJSON("old-logs", story, True)

# traverse
#dc.prnt = True
sim_store = tr.traverse(story, reading, user, rk.guess, dc.best, max_steps)
sim_path = user.path[:]
tr.reset(story, reading, user)

# load logs
log_store = an.walk(story, reading, user, paths_per_reading, max_steps)
log_path = user.path[:]

pt.print_sim_log_comparison(sim_path, log_path)
print("max diff:", max(len(sim_path), len(log_path)))
print("dist:", an.compare_paths(story, sim_store, log_store))
print("similarity of paths:", pt.pc(an.path_similarity(story, sim_store, log_store)))
