import json

class Story:
    def __init__ ( self ):
        self.id = None
        self.name = None
        self.pages = []
        self.conditions = []
        self.functions = []
        self.locations = []
    
    def fromJSON ( self, prnt, filename ):
    # load a story in from a .json file
        # read the file, and convert to a json object
        file = open("json/"+filename+".json", 'r')
        data = file.read()
        file.close()
        if prnt[0]: print(data)
        
        json_object = json.loads(data)
        if prnt[1]: print(json_object)
        
        # id
        self.id = json_object["id"]
        
        # name
        self.name = json_object["name"]
        
        # pages
        for page in json_object["pages"]:
            self.pages.append(Page(
                page["id"],
                page["name"],
                page["functions"],
                page["conditions"]))
        
        # conditions
        for condition in json_object["conditions"]:
            cond = Condition(condition["id"], condition["type"])
            if ( "bool" in condition ): cond.bool = condition["bool"]
            if ( "location" in condition ): cond.location = condition["location"]
            if ( "operand" in condition ): cond.operand = condition["operand"]
            if ( "a" in condition ): cond.a = condition["a"]
            if ( "aType" in condition ): cond.aType = condition["aType"]
            if ( "b" in condition ): cond.b = condition["b"]
            if ( "bType" in condition ): cond.bType = condition["bType"]
            self.conditions.append(cond)
        
        # functions
        for function in json_object["functions"]:
            self.functions.append(Function(
                function["id"],
                function["type"],
                function["conditions"],
                function["variable"],
                function["value"]))

        # locations
        for location in json_object["locations"]:
            self.locations.append(Location(
                location["id"],
                location["type"],
                float(location["lat"]),
                float(location["lon"]),
                float(location["radius"])))
            if prnt[2]: print(self.locations[len(self.locations)-1].id)
        
        if prnt[3]: print("'", self.name, "' is story", self.id, "and contains", len(self.pages), "pages,", len(self.conditions), "conditions,", len(self.functions), "functions &", len(self.locations), "locations.")

class Page:
    def __init__ ( self, id, name, functions, conditions ):
        self.id = id
        self.name = name
        self.functions = functions
        self.conditions = conditions

class Function:
    # TODO: different types of functions' attributes, execution etc.
    def __init__ ( self, id, type, conditions, variable, value ):
        self.id = id
        self.type = type
        self.conditions = conditions
        self.variable = variable
        self.value = value

class Condition:
    # TODO: evaluation
    def __init__ ( self, id, type ):
        self.id = id
        self.type = type
        self.bool = None
        self.location = None
        self.operand = None
        self.a = None
        self.aType = None
        self.b = None
        self.bType = None
    
class Location:
    def __init__ ( self, id, type, lat, lon, radius ):
        self.id = id
        self.type = type
        self.lat = lat
        self.lon = lon
        self.radius = radius

st = Story()
st.fromJSON([False, False, False, True], "Naseem Formatted")
