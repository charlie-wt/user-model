def get ( ls, id ):
    for item in ls:
        if item.id == id: return item
    return None

def index ( ls, id ):
    for i in range(0, len(ls)):
        if ls[i].id == id: return i
    return None

def save ( ls, item ):
    idx = index(ls, item.id)
    if idx is not None:
        ls[idx] = item
        return
    ls.append(item)
