import os
from os.path import join
import customtkinter as ui

class Model:
    def __init__(self):
        pass

class Control: 
    def __init__(self, view, model):
        self.view = view
        self.model = model
        pass

class View(ui): # display and pass to controller only
    def __init__(self, control):
        super().__init__()
        self.control= control
        pass

    
model = Model()
view = View(None)
control = Control(view,model)
view.control = control