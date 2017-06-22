class Collection ():
    def __init__ ( self, data ):
        self.data = data

    def get ( self, id ):
        for item in self.data:
            if item.id == id: return item
        return None
    
    def index ( self, id ):
        for i in range(0, len(self.data)):
            if self.data[i].id == id: return i
        return None

    def save ( self, item ):
        idx = self.index(item.id)
        if idx is not None:
            self.data[i] = item
            return
        self.data.append(item)
    
    def append ( self, item ):
        self.save(item)
        
    def len ( self ):
        return len(self.data)
