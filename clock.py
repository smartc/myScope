import tkinter as tk
from datetime import datetime

class Clock(tk.Label):
    def __init__(self, parent, clock_time = None, suffix=None):
        tk.Label.__init__(self, parent)
        self.stop = False
        if suffix is not None:
            self.suffix = suffix
        else:
             self.suffix = ""
        if clock_time is None:
            self.t1 = None
            self.t2 = None
            self.time = datetime.now().strftime('%H:%M:%S') + self.suffix
        else:
            self.t0 = clock_time
            self.t1 = datetime.now()
            self.t2 = None
            self.time = clock_time.strftime('%H:%M:%S') + self.suffix

        self.configure(text=self.time)

        
    def tick(self):
        if self.t1 is None:
            self.time = datetime.now().strftime('%H:%M:%S') + self.suffix
        else:
            self.t2 = datetime.now()
            self.time = (self.t0 + (self.t2 - self.t1)).strftime('%H:%M:%S') + self.suffix

        self.configure(text=self.time)