import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
sys.path.append(os.path.join(sys.path[0], "models/functions"))
sys.path.append(os.path.join(sys.path[0], "models/conditions"))

import json

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

def storyFromJSON ( filename ):
# load a story in from a .json file
    # read the file, and convert to a json object
    file = open("json/"+filename+".json", 'r')
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
    return story.Story(story_id, story_name, story_pages, story_conditions, story_functions, story_locations)

def pageFromJSON ( json ):
    return page.Page(
            json["id"],
            json["name"],
            json["functions"],
            json["conditions"])

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

def pathsFromJSON ( story, filename ):
# read a log file and return a dictionary containing the paths taken through the
# specified story, per reading.
    # load file
    logfile = open("json/"+filename+".json", 'r')
    logs = logfile.read()
    logfile.close()
    logs_json = json.loads(logs)

    # get a list of event objects for moving through the story
    events = []
    for e in logs_json:
        if e["type"] == "playreadingcard" and e["data"]["storyId"] == story.id:
            events.append(logEventFromJSON(e))
    events.sort(key = lambda e: e.date)

    # convert list into dictionary, arranged per reading
    # dict = { reading_id1 : [ event_1, ..., event_n ], reading_id2 : ... }
    events_per_reading = {}
    for e in events:
        if e.data["readingId"] not in events_per_reading:
            events_per_reading[e.data["readingId"]] = [e]
            continue
        if e.id not in events_per_reading[e.data["readingId"]]:
            events_per_reading[e.data["readingId"]].append(e)
    
    return events_per_reading

def logEventFromJSON ( json ):
    return logevent.LogEvent(
            json["id"],
            json["user"],
            logevent.makeTime(json["date"]),
            json["type"],
            json["data"])
