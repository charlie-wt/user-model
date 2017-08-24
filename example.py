import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import usermodel
from usermodel import importer as imp
from usermodel import ranker as rk
from usermodel import decider as dc
from usermodel import traverser as tr
from usermodel import printer as pt
from usermodel import analyser as an
from usermodel import cache as ch
from usermodel import gui
from usermodel import exporter as ex

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
ppr1 = imp.filteredPathsFromJSON("old-logs", story, legacy=True, prnt=True)
ppr2 = imp.filteredPathsFromJSON("new-logs", story, legacy=False, prnt=True)
paths_per_reading = imp.merge_paths_per_readings(ppr1, ppr2)
cache = ch.cache()

# make path from logs
log_store = tr.traverse_log(story, paths_per_reading)

# predict
sim_store = tr.traverse(story, rk.walk_dist, dc.best, cache=cache, prnt=True)
stores = tr.traverse(story, n=100, cache=cache)

# analyse paths
gui.show_main_three(story, paths_per_reading, stores, sim_store, log_store, rk.walk_dist, cache)

# export data
ex.storeToCSV(log_store, story, prnt=True)
