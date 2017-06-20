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
        
        # locations
        for location in json_object["locations"]:
            self.locations.append(Location(
                location["id"],
                location["type"],
                location["lat"],
                location["lon"],
                location["radius"]))
            if prnt[2]: print(self.locations[len(self.locations)-1].id)

class Location:
    def __init__ ( self, id, type, lat, lon, radius ):
        self.id = id
        self.type = type
        self.lat = lat
        self.lon = lon
        self.radius = radius

st = Story()
st.fromJSON([False, False, True], "Naseem Formatted")
