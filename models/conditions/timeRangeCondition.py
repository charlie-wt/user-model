import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

from datetime import datetime, date, time, timedelta

import condition
import ls

class TimeRangeCondition (condition.Condition):
    def __init__ ( self, id, variable, start, end ):
        self.id = id
        self.type = "timerange"
        self.variable = variable
        self.start = start
        self.end = end

    def check ( self, vars, conds, locs=None, userLoc=None ):
    # check the condition
    # TODO - as yet untested
    # TODO - should probably just return True, as with locationConditions.
        start = getTime(self.start)
        end = getTime(self.end)
        n = datetime.now()

        if start < end:
            within_hours = n.hour > start.hour and n.hour < end.hour
            within_minutes_of_start = n.hour == start.hour and n.minute > start.minute
            within_minutes_of_end = n.hour == end.hour and n.minute < end.minute

            return within_hours or within_minutes_of_start or within_minutes_of_end
        else:
            within_hours_start = n.hour > start.hour
            within_hours_end = n.hour < end.hour
            within_minutes_of_start = n.hour == start.hour and n.minute > start.minute
            within_minutes_of_end = n.hour == end.hour and n.minute < end.minute

            return within_hours_start or within_hours_end or within_minutes_of_start or within_minutes_of_end

    def getTime ( self, str ):
    # convert time string to struct_time
        return time.strptime(str, "%H:%M")
