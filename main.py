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
import exporter as ex

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
#cache = ls.auto_dict()
cache = imp.cacheFromCSV('caches/cache - '+story_name, prnt=True)
rker = rk.logreg

# make path from logs
log_store = an.walk(story, paths_per_reading)

# construct model
rk.reg_no_poi = ml.logreg(story, paths_per_reading, cache, epochs=100, num_folds=1, batch_size=1, exclude_poi=True, prnt=True)
#rk.reg_lin_no_poi = ml.linreg(story, paths_per_reading, cache, epochs=100, num_folds=1, batch_size=1, exclude_poi=True, prnt=True)
#rk.net = ml.nn(story, paths_per_reading, cache, epochs=25, learning_rate=0.001, batch_size=1, num_hidden_layers=10, exclude_poi=True, prnt=True)
#rk.net = ml.nn(story, paths_per_reading, cache, epochs=150, num_hidden_layers=10, batch_size=1, num_folds=10, exclude_poi=True, prnt=True)

# predict
rk.prnt = False
sim_store = tr.traverse(story, rker, dc.best, cache=cache, prnt=False, max_steps=50)
rk.prnt = False
stores = tr.traverse_many(story, n=100, ranker=rker, cache=cache)

# analyse paths
#gui.show_main_three(story, paths_per_reading, stores, sim_store, log_store, rker, cache)
#gui.show_all(story, paths_per_reading, stores, sim_store, log_store, rker, cache)

# export data
#ex.pathToCSV(log_store, prnt=True)
#ex.storesToJSON(log_store, 'log_store.json',  prnt=True)
