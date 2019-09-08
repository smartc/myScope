from clock import Clock
from datetime import datetime
import tkinter as tk
from threading import Thread
from time import sleep

def exit_event():
	global app
	app.stop = True
	app.destroy()

def watcher(root):
    while not root.stop:
        root.data.scope_time.tick()
        sleep(200/1000)

class DataFrame(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		
		WIDTH = 300
		HEIGHT = 200
		PAD = 3
		FONT = "-*-lucidatypewriter-medium-r-*-*-*-140-*-*-*-*-*-*"

		#######################################
		#testing variables
		SCP_LAT = 50.5555
		SCP_LON = -114.3014
		SCP_ALT = 1250.0
		SCP_DATE = datetime(2018, 9, 1, 15, 33, 23)
		#######################################

		self.topFrame = tk.Frame(self, width=WIDTH-10, height=50, pady=PAD)
		self.centerFrame = tk.Frame(self, bg='gray', width=WIDTH-10, height=HEIGHT-120, padx=PAD, pady=PAD)
		self.btmFrame = tk.Frame(self, bg='white', width=WIDTH-10, height=50, pady=PAD)

		#layout main containers
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.topFrame.grid(row=0, sticky="ew")
		self.centerFrame.grid(row=1, sticky="nsew")
		self.btmFrame.grid(row=3, sticky="ew")


		#setup headers
		self.topFrame.grid_columnconfigure(0, weight=1)
		self.topFrame.grid_columnconfigure(1, weight=1)

		scope_hdr = tk.Label(self.topFrame, text='Scope')
		gps_hdr = tk.Label(self.topFrame, text='GPS')

		scope_hdr.grid(row=0, column=0, sticky="ew")
		gps_hdr.grid(row=0, column=1, sticky="ew")

		#setup internal panels
		self.centerFrame.grid_rowconfigure(0, weight=1)
		self.centerFrame.grid_columnconfigure(0, weight=1)
		self.centerFrame.grid_columnconfigure(1, weight=1)

		self.left_panel = tk.Frame(self.centerFrame, bg='blue', width=WIDTH/2, height=HEIGHT-120)
		self.right_panel = tk.Frame(self.centerFrame, bg='green', width=WIDTH/2, height=HEIGHT-120, padx=PAD, pady=PAD)

		self.left_panel.grid(row=0, column=0, sticky="nsew")
		self.right_panel.grid(row=0, column=1, sticky="nsew")

		#setup scope labels:
		lat1 = tk.Label(self.left_panel, text="LAT:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		lon1 = tk.Label(self.left_panel, text="LON:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		alt1 = tk.Label(self.left_panel, text="ALT:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		time1 = tk.Label(self.left_panel, text="TIME:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		date1 = tk.Label(self.left_panel, text="DATE:", anchor="e", width=10, font=FONT, padx=3, pady=3)

		lat1.grid(row=0, column=0, sticky="ew")
		lon1.grid(row=1, column=0, sticky="ew")
		alt1.grid(row=2, column=0, sticky="ew")
		time1.grid(row=3, column=0, sticky="ew")
		date1.grid(row=4, column=0, sticky="ew")


		#setup scope data pane
		self.left_panel.grid_columnconfigure(1, weight=1)

		self.scope_lat = tk.Label(self.left_panel, text="{:<+.4f} °".format(SCP_LAT), font=FONT, relief="groove", padx=3, pady=3)
		self.scope_lon = tk.Label(self.left_panel, text="{:<+.4f} °".format(SCP_LON), font=FONT, relief="groove", padx=3, pady=3)
		self.scope_alt = tk.Label(self.left_panel, text="{:<+,.1f} m".format(int(SCP_ALT)), font=FONT, relief="groove", padx=3, pady=3)

		self.scope_time = Clock(self.left_panel, SCP_DATE, " UTC")
		self.scope_time.configure(font=FONT, relief="groove", padx=3, pady=3)
	
		self.scope_date = tk.Label(self.left_panel, text="{:%Y-%m-%d}".format(SCP_DATE), font=FONT, relief="groove", padx=3, pady=3)

		self.scope_lat.grid(row=0, column=1, sticky="ew")
		self.scope_lon.grid(row=1, column=1, sticky="ew")
		self.scope_alt.grid(row=2, column=1, sticky="ew")
		self.scope_time.grid(row=3, column=1, sticky="ew")
		self.scope_date.grid(row=4, column=1, sticky="ew")




if __name__ == "__main__":
	global app
	app = tk.Tk()
	app.protocol("WM_DELETE_WINDOW", exit_event)
	app.stop = False
	app.data = DataFrame(app)
	app.data.pack()

	watcherThread = Thread(target=watcher, kwargs={'root': app}, name="tick_tock")
	watcherThread.start()
	app.mainloop()
