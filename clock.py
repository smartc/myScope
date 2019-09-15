import tkinter as tk
from datetime import datetime

class Clock(tk.Label):
    def __init__(self, parent, clock_time = None, suffix=None, format='%H:%M:%S'):
        tk.Label.__init__(self, parent)
        self.format = format
        self.stop = False
        if suffix is not None:
            self.suffix = suffix
        else:
             self.suffix = ""
        if clock_time is None:
            self.t1 = None
            self.t2 = None
            self.time = datetime.now().strftime(format) + self.suffix
        else:
            self.t0 = clock_time
            self.t1 = datetime.now()
            self.t2 = None
            self.time = clock_time.strftime(format) + self.suffix

        self.configure(text=self.time)

        
    def tick(self, format='%H:%M:%S'):
        if self.t1 is None:
            self.time = datetime.now().strftime(format) + self.suffix
        else:
            self.t2 = datetime.now()
            self.time = (self.t0 + (self.t2 - self.t1)).strftime(format) + self.suffix

        self.configure(text=self.time)

    def set(self, set_time):
        self.t0 = set_time
        self.t1 = datetime.now()
        self.t2 = None
        self.time = set_time.strftime(self.format) + self.suffix
        self.configure(text=self.time)