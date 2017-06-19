import tkinter as tk

class Window (tk.Frame):
    def __init__ ( self, parent ):
        tk.Frame.__init__(self, parent)
        
        self.parent = parent
        
        self.initUI()
    
    def initUI ( self ):
        self.parent.title("graph")
        self.pack(fill=tk.BOTH, expand=1)

def make ():
    top = tk.Tk()
    top.geometry("250x150")
    app = Window(top)
    top.mainloop()

#def graph ( ns ):
    
