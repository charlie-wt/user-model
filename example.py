import usermodel as um

# === SETUP ===
# load our story from its .json file, store it in a Story object
story = um.importer.story_from_json('json/Notes on an Illegible City')
# load two user logs from different files.
paths_per_reading = um.importer.filtered_paths_from_json(['json/old-logs', 'json/new-logs'], story, prnt=True)
# create a cache, to store our calculated heuristic values
cache = um.cache.Cache()

# === LOG-BASED PATH ===
# traverse the story, where at each point we choose the most popular next page.
log_store = um.traverser.traverse_log(story, paths_per_reading)

# === TRAIN MACHINE LEARNING MODEL ===
# train a neural network. - NOTE: this will take a long time if 'exclude_poi' is False (which it is by default)
#um.ml.nn(paths_per_reading, cache, prnt=True)

# === SIMULATE SOME READINGS ===
# choose our ranker and decider functions
myranker = um.ranker.walk_dist  # if you want to use the neural network, just change this to um.ranker.nn
mydecider = um.decider.best
# do one reading, using our chosen ranker and decider.
sim_store = um.traverser.traverse(story, myranker, mydecider, cache=cache, prnt=True)
# do 100 readings randomly, to try and spot any unreachable pages.
stores = um.traverser.traverse(story, n=100, cache=cache)

# === GUI ===
# create a GUI window to display the three main comparison metrics.
um.gui.show_main_three(story, paths_per_reading, stores, sim_store, log_store, myranker, cache)

# === EXPORT DATA ===
# export our simulated reading (with both the path, and the choices at each point) to a .csv file.
um.exporter.store_to_csv(sim_store, story, prnt=True)
# export our cache to a .csv file. This can be loaded in next time from the start.
um.exporter.cache_to_csv(cache, prnt=True)
