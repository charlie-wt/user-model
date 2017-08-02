import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import importer as imp
import ranker as rk
import decider as dc
import traverser as tr
import printer as pt
import analyser as an
import ls
import gui
import mapping as mp

names = ["A Walk In The Park",                  #  0
         "Butterflies",                         #  1
         "Connections",                         #  2
         "Fallen branches",                     #  3
         "Fire Fire",                           #  4
         "Naseem - The Pharaohs Attendant",     #  5
         "Notes on an Illegible City",          #  6
         "Seeker of Secrets",                   #  7
         "Six Stories Of Southampton",          #  8
         "The Bournemouth Triangle",            #  9
         "The Destitute and The Alien",         # 10
         "The Pathways of Destiny",             # 11
         "The Tale of Molly DeVito",            # 12
         "The Titanic Criminal In Southampton"] # 13



story_name = names[6]

max_steps = 50



# create/load stuff
story = imp.storyFromJSON(story_name)
epr = imp.pathEventsFromJSON("old-logs", story)
paths_per_reading = an.filter_readings(story, epr, prnt=True)

# traverse
sim_store = tr.traverse(story, rk.alt, dc.best, max_steps)
sim_path = [ r.page for r in sim_store ]

# load logs
log_store = an.walk(story, paths_per_reading, max_steps)
log_path = [ r.page for r in log_store ]

# analyse paths
#pt.print_sim_log_comparison(sim_path, log_path)
err = tr.step_predict(story, log_store, rk.guess)

stores = tr.traverse_many(story, 10, rk.walk_dist)
gui.show_all(story, paths_per_reading, stores, sim_store, log_store, err)
