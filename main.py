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
import ml

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



# create/load stuff
story = imp.storyFromJSON(story_name)
epr = imp.pathEventsFromJSON("old-logs", story)
paths_per_reading = an.filter_readings(story, epr)
cache = ls.auto_dict()

# load logs
log_store = an.walk(story, paths_per_reading)
log_path = [ r.page for r in log_store ]

# predict
sim_store = tr.traverse(story, rk.rand, dc.best, cache=cache)
sim_path = [ r.page for r in sim_store ]

ml.formalise(story, list(paths_per_reading.values())[0], cache, True, False)
#gui.measure_ranker(story, paths_per_reading, rk.walk_dist, cache)

#err = tr.step_predict(story, log_store, rk.walk_dist, cache)
#stores = tr.traverse_many(story, ranker=rk.walk_dist, cache=cache)

# analyse paths
#gui.show_all(story, paths_per_reading, stores, sim_store, log_store, err)
