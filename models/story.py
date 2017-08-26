import math
import re
import base

class Story (base.Base):
    ''' A story to be read '''
    def __init__ ( self, id, name, pages, conditions, functions, locations ):
        self.id = id
        self.name = name
        self.pages = pages
        self.conditions = conditions
        self.functions = functions
        self.locations = locations

    def idf ( self, term ):
        ''' inverse document frequency of a term, over all pages. '''
        num_docs = 1
        for p in self.pages:
            doc = p.text.lower().split()
            doc = [ re.sub('[\W_]+', '', w) for w in doc ]
            if term in doc: num_docs += 1

        return math.log(len(self.pages) / num_docs)
