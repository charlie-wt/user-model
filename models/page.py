import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base
import ls

class Page (base.Base):
    def __init__ ( self, id, name, functions, conditions ):
        self.id = id
        self.name = name
        self.functions = functions
        self.conditions = conditions
        self.visible = False

    def update ( self, story, reading, user ):
    # see if this page should be visible
        for c in self.conditions:
            if not ls.get(story.conditions, c).check(reading.vars, story.conditions):
                self.visible = False
                return
        self.visible = True

    def execute_functions ( self, story, reading, user ):
    # execute all the functions on this page
        for f in self.functions:
            ls.get(story.functions, f).execute(story, reading, user)

    def getLoc( self, story ):
    # get the location of this page (via location condition)
        for cond_id in self.conditions:
            cond = ls.get(story.conditions, cond_id)
            if cond.type == "location":
                page_loc = ls.get(story.locations, cond.location)
                loc = (page_loc.lat, page_loc.lon)
                return loc
        return None

def update_all ( pages, story, reading, user ):
# update a bunch of pages at once
    visible = []
    for page in pages:
        page.update( story, reading, user )
        if page.visible: visible.append(page)
    return visible

def fromLogEvent ( story, le ):
# turn 'go to page' log event into a page
    return ls.get(story.pages, le.data["cardId"])

def fromLogEvents ( story, les ):
# turn 'go to page' log events into pages
    pages = []
    for le in les:
        new_page = fromLogEvent(story, le)
        if new_page is not None: pages.append(new_page)
    return pages

def last ( page, visible=None ):
# is this page the last in its story?
    check = \
           page == None \
        or page == 0 \
        or page.name == "Finish" \
        or page.name == "Finish Story"
    if visible is not None: check = check or len(visible) == 0
    return check
