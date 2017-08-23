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

##### importer ###############
# a set of functions to import various structures from json files.
##############################

def storyFromJSON ( filename, prnt=False ):
# load a story in from a .json file
    # read the file, and convert to a json object
    file = open("json/"+filename+".json", 'r', encoding='utf-8')
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
        story_pages.append(pageFromJSON(page))

    # functions
    story_functions = []
    for function in json_object["functions"]:
        story_functions.append(functionFromJSON(function))

    # conditions
    story_conditions = []
    for condition in json_object["conditions"]:
        story_conditions.append(conditionFromJSON(condition))

    # locations
    story_locations = []
    for location in json_object["locations"]:
        story_locations.append(locationFromJSON(location))

    # combine into story
    sto = story.Story(story_id,
                      story_name,
                      story_pages,
                      story_conditions,
                      story_functions,
                      story_locations)

    if prnt: pt.print_story(sto)
    return sto

def pageFromJSON ( json ):
    return page.Page(
            json["id"],
            json["name"],
            json["functions"],
            json["conditions"],
            json["content"])

def functionFromJSON ( json ):
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

def conditionFromJSON ( json ):
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

def locationFromJSON ( json ):
    return location.Location(
            json["id"],
            json["type"],
            float(json["lat"]),
            float(json["lon"]),
            float(json["radius"]))

def pathEventsFromJSON ( filename, story=None, legacy=False, prnt=False):
# read a log file and return a dictionary containing the paths taken through the
# specified story, per reading.
    # load file
    logfile = open("json/"+filename+".json", 'r', encoding='utf-8')
    logs = logfile.read()
    logfile.close()
    logs_json = json.loads(logs)
    read_page_tag = 'playreadingcard' if legacy else 'PageRead'

    # get a list of event objects for moving through the story
    events = []
    for e in logs_json:
        if e["type"] == read_page_tag:
            if story is not None:
                if e["data"]["storyId"] == story.id:
                    events.append(logEventFromJSON(e, legacy))
            else:
                events.append(logEventFromJSON(e, legacy))
    events.sort(key = lambda e: e.date)

    # convert list into dictionary, arranged per reading
    # epr = { reading_id1 : [ event_1, ..., event_n ], reading_id2 : ... }
    epr = {}
    for e in events:
        if e.data["readingId"] not in epr:
            epr[e.data["readingId"]] = [e]
            continue
        if e.id not in epr[e.data["readingId"]]:
            epr[e.data["readingId"]].append(e)

    if prnt:
        print("Found", len(epr), "readings", end="")
        if story is not None: print(" for", story.name+".")
        else: print(".")

    return epr

def pathPagesFromJSON ( filename, story, legacy=False, prnt=False ):
# same as pathEventsFromJSON, but the dictionary contains lists of pages,
# instead of lists of events
    epr = pathEventsFromJSON(filename, story, legacy, False)
    ppr = {}

    for r in epr:
        pages = page.fromLogEvents(story, epr[r], legacy)
        ppr[r] = pages

    if prnt: print("Found", len(ppr), "readings for", story.name+".")
    return ppr

def filteredPathsFromJSON ( filename, story, legacy=False, prnt=False ):
    epr = pathEventsFromJSON(filename, story, legacy, False)
    return an.filter_readings(story, epr, legacy=legacy, prnt=prnt)

def logEventFromJSON ( json, legacy=False ):
    return logevent.LogEvent(
            json["id"],
            json["user"],
            logevent.makeTime(json["date"], legacy),
            json["type"],
            json["data"])

def cacheFromCSV ( filename, prnt=False ):
# read in a heuristics cache from a .csv file.
    filename = ex.clip_filename(filename, 'csv')
    cache = ls.auto_dict()

    def recurse ( cache, row ):
    # add elements of the csv row to the cache deeply
        if len(row) > 2:
            recurse(cache[row[0]], row[1:])
        else:
            cache[row[0]] = to_num(row[1])

    def to_num ( string ):
    # try and convert a string to a number (but leave it if you can't)
        try:
            return int(string)
        except:
            try:
                return float(string)
            except:
                return string

    with open(filename+'.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            recurse(cache, row)

    if prnt:
        print('imported cache = [')
        pt.print_cache(cache)
        print(']')

    return cache

def cacheFromJSON ( filename, prnt=False ):
# TODO - untested
    filename = ex.clip_filename(filename, 'json')
    with open(filename+".json", 'r', encoding='utf-8') as jsonfile:
        data = jsonfile.read()
        jsonfile.close()
        json_object = json.loads(data)

        cache = ls.auto_dict()
        cache.update(json_object)

        if prnt:
            print('imported cache = [')
            pt.print_cache(cache)
            print(']')

       return cache

def merge_paths_per_readings ( ppr1, ppr2 ):
# put two paths_per_reading dictionaries together.
# TODO - extend this to arbitrary length.
    new = ppr1.copy()
    new.update(ppr2)
    return new
