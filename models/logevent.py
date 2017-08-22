from datetime import datetime

import base

class LogEvent (base.Base):
    def __init__ ( self, id, user, date, type, data ):
        self.id = id
        self.user = user
        self.date = date
        self.type = type
        self.data = data

def makeTime ( string, legacy=False ):
    if legacy:
        return datetime.strptime(string, "%Y-%m-%dT%X.000Z")
    else:
        return datetime.strptime(string[:-5], "%Y-%m-%dT%X")
