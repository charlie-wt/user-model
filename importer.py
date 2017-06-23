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

def storyFromJSON ( filename, prnt ):
# load a story in from a .json file
    # read the file, and convert to a json object
    file = open("json/"+filename+".json", 'r')
    data = file.read()
    file.close()
    if prnt[0]: print(".TEXT INPUT.\n"+data)

    json_object = json.loads(data)
    if prnt[1]:
        print(".LOADED JSON.")
        print(json_object)

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
    if prnt[2]: print(".CONDITIONS.")
    for condition in json_object["conditions"]:
        story_conditions.append(conditionFromJSON(condition))
        if prnt[2]: print(story_conditions[len(story_conditions)-1].id)
    if prnt[2]: print()

    # printing shenanigens
    if prnt[3]: print(".EXISTENCE OF THE CONDITIONS OF FUNCTIONS.")
    if prnt[3]:
        cond_ids = (cond.id for cond in story_conditions)
        for f in story_functions:
            if prnt[3]:
                cs = f.conditions
                if len(cs) > 0:
                    exists = True
                    for c in cs:
                        if c not in cond_ids: exists = False
                    print("function", f.id, "has conditions", cs, ": do they exist? ->", exists)
    if prnt[3]: print()

    # locations
    story_locations = []
    for location in json_object["locations"]:
        story_locations.append(locationFromJSON(location))

    if prnt[4]: print(".STORY INFO.\n'", story_name, "' is story", story_id, "and contains", len(story_pages), "pages,", len(story_conditions), "conditions,", len(story_functions), "functions &", len(story_locations), "locations.")

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
        return setFunction.SetFunction(
                json["id"],
                json["conditions"],
                json["variable"],
                (json["value"] == "true"))  # necessary to do this? also, are ALL values bools?
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
