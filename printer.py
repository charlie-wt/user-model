import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import location as lc
import ls

def print_story ( story, reading=None ):
# print basic story info
    print("'"+story.name+"' is story", story.id, "and contains", len(story.pages), "pages,", len(story.conditions), "conditions,", len(story.functions), "functions", end="")
    if reading is not None:
        print(",", len(story.locations), "locations &", len(reading.vars), "variables.")
    else:
        print(" &", len(story.locations), "locations.")
    print()

def print_visible ( vis, story, us ):
# print the list of visible pages in a story
    for p in vis:
        page_loc = p.getLoc(story)
        if page_loc is not None:
            dist = lc.metres(us.lat(), us.lon(), page_loc[0], page_loc[1])
            print("\t", p.name + "\t:\t" + p.id + " -> " + str(dist) + " metres away.")
        else:
            print("\t", p.name + "\t:\t" + p.id + ", which can be accessed from anywhere.")

def print_path ( story, path ):
# print the pages in a path
    print("Path through "+story.name+":")
    for p in path: print(p.name)
    print()
    
def print_log_paths ( story, paths ):
# print paths per reading, as output by log importer
    print("Paths through "+story.name+", per reading:")
    for r in paths.keys():
        print("reading "+r+":")
        for e in paths[r]:
            print("\t", e.date)
    print()

def print_event_path ( story, path ):
# print the path of events taken through a story by a real user
    if len(path) is 0: return

    print("Path taken by user through "+story.name+":")
    for pg in path:
        page = ls.get(story.pages, pg.data["cardId"])
        print(pg.date, ":", pg.data["cardId"], ": ", end="")
        if page is not None:
            print(page.name)
        else:
            print(pg.data["cardLabel"], "("+pg.data["cardId"]+")", "(NOT FOUND)")
    print()
