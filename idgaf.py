import os
from os.path import join
import customtkinter as ui

class View(ui):
    def __init__(self, control):
        super().__init__()
        self.control= control
        pass

class Control: 
    def __init__(self, view, model):
        self.view = view
        self.model = model
        pass

class Model:
    def __init__(self):
        pass

    
model = Model()
view = View(None)
control = Control(view,model)
view.control = control