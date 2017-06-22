import base

class Page (base.Base):
    def __init__ ( self, id, name, functions, conditions ):
        self.id = id
        self.name = name
        self.functions = functions
        self.conditions = conditions
        self.visible = False

    def update ( self, vars, conds, locs, userLoc ):
    # see if this page should be visible
        for c in self.conditions:
            if not conds.get(c).check(vars, conds):
                self.visible = False
                return
        self.visible = True

    def execute_functions ( self, story_id, reading_id, vars, conds, locs, userLoc, functions ):
    # execute all the functions on this page
        for f in this.functions:
            functions.get(f).execute(story_id, reading_id, vars, conds, functions, locs, userLoc)
