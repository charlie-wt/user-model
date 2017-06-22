class Collection ():
    def __init__ ( self, data ):
        self.data = data

    def get ( self, id ):
        for item in data:
            if item.id == id: return item
        return None
    
    def index ( self, id ):
        for i in range(0, len(data)):
            if data[i].id == id: return i
        return None

    def save ( self, item ):
        idx = self.index(item.id)
        if idx is not None:
            data[i] = item
            return
        data.append(item)
