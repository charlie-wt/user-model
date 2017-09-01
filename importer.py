import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
sys.path.append(os.path.join(sys.path[0], "models/functions"))
sys.path.append(os.path.join(sys.path[0], "models/conditions"))

import json
import csv
from datetime import timedelta

import story
import page
import location
import function
import chainFunction
import incrementFunction
import setFunction
import setTimestampFunction
import condition
import checkCondition
import comparisonCondition
import locationCondition
import logicalCondition
import timePassedCondition
import timeRangeCondition
import variable
import logevent
import printer as pt
import analyser as an
import exporter as ex
import ls
import cache as ch
import record as rc
import user as us
import reading as rd

'''
importer

a set of functions to import various structures from json files.
'''

def story_from_json ( filename, prnt=False ):
    ''' load a story in from a .json file. '''
    # read the file, and convert to a json object
    filename = ex.clip_filename(filename, 'json')
    file = open(filename+".json", 'r', encoding='utf-8')
    data = file.read()
    file.close()

    json_object = json.loads(data)

    # id
    story_id = json_object["id"]

    # name
    story_name = json_object["name"]

    # pages
    story_pages = []
    for page in json_object["pages"]:
        story_pages.append(page_from_json(page))

    # functions
    story_functions = []
    for function in json_object["functions"]:
        story_functions.append(function_from_json(function))

    # conditions
    story_conditions = []
    for condition in json_object["conditions"]:
        story_conditions.append(condition_from_json(condition))

    # locations
    story_locations = []
    for location in json_object["locations"]:
        story_locations.append(location_from_json(location))

    # combine into story
    sto = story.Story(story_id,
                      story_name,
                      story_pages,
                      story_conditions,
                      story_functions,
                      story_locations)

    if prnt: pt.print_story(sto)
    return sto

def stories_from_json ( filenames, prnt=False ):
    ''' load a list of stories from their json files. '''
    stories = []
    for name in filenames:
        stories.append(story_from_json(name, prnt=False))
    if prnt: print('loaded', len(filenames), 'stories from json.')
    return stories

def page_from_json ( json ):
    return page.Page(
            json["id"],
            json["name"],
            json["functions"],
            json["conditions"],
            json["pageTransition"],
            json["content"])

def function_from_json ( json ):
    type = json["type"]
    if   ( type == "increment" ):
        return incrementFunction.IncrementFunction(
                json["id"],
                json["conditions"],
                json["variable"],
                json["value"])
    elif ( type == "set" ):
        value = None
        if json["value"] == "true" or json["value"] == "false":
            value = (json["value"] == "true")
        elif json["value"].isdigit():
            value = int(json["value"])
        else: value = json["value"]
        return setFunction.SetFunction(
                json["id"],
                json["conditions"],
                json["variable"],
                value)
    elif ( type == "chain" ):
        return chainFunction.ChainFunction(
                json["id"],
                json["conditions"],
                json["functions"])
    elif ( type == "settimestamp" ):
        return setTimestampFunction.SetTimestampFunction(
                json["id"],
                json["conditions"],
                json["variable"])
    else: return None

def condition_from_json ( json ):
    type = json["type"]
    if   ( type == "check" ):
        return checkCondition.CheckCondition(
                json["id"],
                json["a"],
                json["b"],
                json["aType"],
                json["bType"],
                json["operand"])
    elif ( type == "comparison" ):
        return comparisonCondition.ComparisonCondition(
                json["id"],
                json["a"],
                json["b"],
                json["aType"],
                json["bType"],
                json["operand"])
    elif ( type == "location" ):
        return locationCondition.LocationCondition(
                json["id"],
                (json["bool"] == "true"),
                json["location"])
    elif ( type == "logical" ):
        return logicalCondition.LogicalCondition(
                json["id"],
                json["operand"],
                json["conditions"])
    elif ( type == "timepassed" ):
        return timePassedCondition.TimePassedCondition(
                json["id"],
                json["variable"],
                json["minutes"])
    elif ( type == "timerange" ):
        return timeRangeCondition.TimeRangeCondition(
                json["id"],
                json["variable"],
                json["start"],
                json["end"])
    else:
        return None

def location_from_json ( json ):
    return location.Location(
            json["id"],
            json["type"],
            float(json["lat"]),
            float(json["lon"]),
            float(json["radius"]))

def path_events_from_json ( filename, stories, prnt=False):
    ''' read a log file and return a dictionary containing the paths taken
    through the specified story, per reading.
    '''
    if type(stories) is not list: stories = [stories]
    legacy = None
    # load file
    filename = ex.clip_filename(filename, 'json')
    logfile = open(filename+".json", 'r', encoding='utf-8')
    logs = logfile.read()
    logfile.close()
    logs_json = json.loads(logs)

    def is_read_page ( event_type ):
        ''' figure out if this event is a 'page read' event, and if the log is
        in the legacy format or not.
        '''
        nonlocal legacy
        if legacy is not None:
            return event_type == 'playreadingcard' if legacy else event_type == 'PageRead'
        else:
            if event_type == 'playreadingcard':
                legacy = True
                return True
            elif event_type == 'PageRead':
                legacy = False
                return True
            return False

    # get a list of event objects for moving through the story
    story_ids = [ s.id for s in stories ]
    events = []
    for e in logs_json:
        if is_read_page(e["type"]):
            if e["data"]["storyId"] in story_ids:
                events.append(log_event_from_json(e, legacy))
    events.sort(key = lambda e: e.date)

    # convert list into dictionary, arranged per reading
    # epr = { reading_id1 : [ event_1, ..., event_n ], reading_id2 : ... }
    epr = {}
    for e in events:
        if ls.get(epr, e.data["readingId"]) is None:
            story = ls.get(stories, e.data["storyId"])
            reading = rd.Reading(e.data["readingId"], story)
            epr[reading] = [e]
            continue
        reading = ls.get(epr, e.data["readingId"])
        if e.id not in epr[reading]:
            epr[reading].append(e)

    if prnt:
        print("Found", len(epr), "readings", end="")
        if len(stories) == 1: print(" for", stories[0].name+".")
        else: print(".")

    return epr

def log_event_from_json ( json, legacy ):
    return logevent.LogEvent(
            json["id"],
            json["user"],
            logevent.make_time(json["date"], legacy),
            json["type"],
            json["data"])

def path_pages_from_json ( filename, stories, prnt=False ):
    ''' same as path_events_from_json, but the dictionary contains lists of
    pages, instead of lists of events.
    '''
    epr = path_events_from_json(filename, stories, False)
    ppr = {}

    for r in epr:
        story = r.story
        pages = page.from_log_events(story, epr[r])
        ppr[r] = pages

    if prnt:
        print("Found", len(ppr), "readings", end="")
        if len(stories) == 1: print(" for", stories[0].name+".")
        else: print(".")
    return ppr

def filtered_paths_from_json ( filenames, stories, demo_mode=False,
                               speed_threshold=5, prnt=False ):
    ''' combine path_events_from_json with analyser.filter_paths. '''
    if type(filenames) is not list: filenames = [filenames]
    if type(stories) is not list: stories = [stories]

    def fun ( filename ):
        epr = path_events_from_json(filename, stories, prnt=False)
        return an.filter_readings(epr, demo_mode, speed_threshold, prnt=False)

    ppr = {}
    for name in filenames:
        ppr.update(fun(name))

    if prnt:
        pt.print_filtered_paths_count(stories, ppr, demo_mode)

    return ppr

def cache_from_csv ( filename, prnt=False ):
    ''' read in a heuristics cache from a .csv file. '''
    filename = ex.clip_filename(filename, 'csv')
    cache = ch.Cache()

    def recurse ( cache, row ):
    # add elements of the csv row to the cache deeply
        if len(row) > 2:
            recurse(cache[row[0]], row[1:])
        else:
            cache[row[0]] = num(row[1])

    with open(filename+'.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            recurse(cache, row)

    if prnt:
        print('imported cache = [')
        pt.print_cache(cache)
        print(']')

    return cache

def cache_from_json ( filename, prnt=False ):
    filename = ex.clip_filename(filename, 'json')
    with open(filename+".json", 'r', encoding='utf-8') as jsonfile:
        data = jsonfile.read()
        jsonfile.close()
        json_object = json.loads(data)

        cache = ch.Cache()
        cache.update(json_object)

    if prnt:
        print('imported cache = [')
        pt.print_cache(cache)
        print(']')

    return cache

def caches_from_csv (filenames, prnt=False ):
    ''' load a list of caches from their csv files. '''
    caches = []
    for name in filenames:
        caches.append(cache_from_csv(name, prnt=False))
    if prnt: print('loaded', len(filenames), 'caches from csv.')
    return caches

def caches_from_json (filenames, prnt=False ):
    ''' load a list of caches from their json files. '''
    caches = []
    for name in filenames:
        caches.append(cache_from_json(name, prnt=False))
    if prnt: print('loaded', len(filenames), 'caches from json.')
    return caches

def stores_from_csv ( filename, story, prnt=False ):
    # load file
    filename = ex.clip_filename(filename, 'csv')
    stores = []
    with open(filename+".csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # discard the first row
        next(reader)

        # the list of page ids used by the options dictionaries is the second row.
        pages = next(reader)[1:]
        pages[pages.index('---quit---')] = 0

        # read the remaining rows, containing the actual steps of the reading.
        store = []
        for row in reader:
            # if we hit an empty line, start a new reading.
            if len(row) == 0:
                stores.append(store)
                store = []
                continue

            # get current page
            current_page = None
            if row[0] != '---':
                current_page = ls.get(story.pages, row[0])

            # get options for next page
            options = {}
            for i in range(len(row[1:])):
                row_idx = i+1
                page_id = pages[i]
                op_page = ls.get(story.pages, page_id)
                options[op_page] = row[row_idx]

            # put it all together
            record = rc.Record(current_page, options)
            store.append(record)

    if prnt: print('imported', len(stores), 'store'+ \
                   ('s' if len(stores) > 1 else ''), 'from csv.')
    return stores

def store_from_csv ( filename, story, prnt=False ):
    filename = ex.clip_filename(filename, 'csv')
    stores = stores_from_csv(filename, story, prnt=False)
    store = stores[0]
    if prnt: print('imported store from csv of length', str(len(store))+'.')
    return store

def stores_from_json ( filename, story, prnt=False ):
    filename = ex.clip_filename(filename, 'json')
    with open(filename+".json", 'r', encoding='utf-8') as jsonfile:
        data = jsonfile.read()
        jsonfile.close()
        json_object = json.loads(data)

        stores = []
        for json_store in json_object:
            store = []
            for json_record in json_store:
                current_page = ls.get(story.pages, json_record['page'])
                options = {}
                for p in json_record['options']:
                    op_page = ls.get(story.pages, p)
                    options[op_page] = json_record['options'][p]

                record = rc.Record(current_page, options)
                store.append(record)
            stores.append(store)

        if prnt: print('imported', len(stores), 'store'+ \
                       ('s' if len(stores) > 1 else ''), 'from json.')

    return stores

def merge_paths_per_readings ( pprs ):
    ''' put two paths_per_reading dictionaries together. '''
    new = pprs[0].copy()
    for ppr in pprs:
        new.update(ppr)
    return new

def num ( string ):
    ''' try and convert a string to a number (but leave it if you can't). '''
    try:
        return int(string)
    except:
        try:
            return float(string)
        except:
            return string
