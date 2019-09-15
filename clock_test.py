from clock import Clock
from datetime import datetime
import tkinter as tk
import threading
import ctypes
from time import sleep
from serial_tools import serial_ports
from micropyGPS import MicropyGPS
from serial import Serial
from pytz import UTC

FONT = "-*-lucidatypewriter-medium-r-*-*-*-140-*-*-*-*-*-*"


def exit_event():
	global app
	global watcherThread
	watcherThread.raise_exception()
	sleep(0.25)
	app.destroy()
	watcherThread.join()

class comPortDialog(tk.Toplevel):
	def __init__(self, parent):
		tk.Toplevel.__init__(self, parent)

		self.coms = serial_ports()
		self.previous_port = parent.port
		self.selected_port = tk.StringVar()
		if parent.port is None:
			self.selected_port.set(None)
		else:
			self.selected_port.set(parent.port)

		self.label = tk.Label(self, text="Select COM Port:")
		self.options = tk.OptionMenu(self, self.selected_port, *self.coms)
		self.ok_button = tk.Button(self, text="OK", command=self.on_ok)
		self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel)

		self.label.pack(side="top", fill="x")
		self.options.pack(side="top", fill="x")
		self.ok_button.pack(side="right")
		self.cancel_button.pack(side="left")

	def on_ok(self, event=None):
		self.destroy()

	def cancel(self, event=None):
		self.selected_port.set(self.previous_port)
		self.destroy()

	def show(self):
		self.wm_deiconify()
		self.options.focus_force()
		self.wait_window()
		return self.selected_port.get()


class Worker(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name

	def run(self):
		global app
		try:
			while not app.stop:
				app.data.scope_time.tick()
				app.data.scope_date.tick('%Y-%m-%d')
				if app.gpsdata.gps_valid:
					app.gpsdata.time.tick()
					app.gpsdata.date.tick('%Y-%m-%d')
				sleep(0.2)
		finally:
			print("terminating {}".format(self.name))

	def get_id(self):
		if hasattr(self, '_thread_id'):
			return self._thread_id
		for id, thread in threading._active.items():
			if thread is self:
				return id

	def raise_exception(self):
		global app
		app.stop = True
		thread_id = self.get_id()
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
			ctypes.py_object(SystemExit))
		if res > 1: 
			ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
			print('Exception raise failure')
		
def watcher():
	global app
	while not app.stop:
		app.data.scope_time.tick()
		app.data.scope_date.tick('%Y-%m-%d')
		if app.gpsdata.gps_valid:
			app.gpsdata.time.tick()
			app.gpsdata.date.tick('%Y-%m-%d')
		sleep(200/1000)

class GpsFrame(tk.Frame):
	def __init__(self, parent):
		global FONT
		tk.Frame.__init__(self, parent)

		#######################################
		#testing variables
		self.gps_lat = 50.699420
		self.gps_lon = -114.005746
		self.gps_alt = 1107.0
		self.gps_date = datetime(1999, 1, 1, 0, 0, 0)
		#######################################		

		self.port = None
		self.gps_connected = False
		self.gps = None
		self.gps_parser = MicropyGPS()
		self.gps_sentence = ""
		self.gps_valid = False

		#setup GPS frame
		lat2 = tk.Label(parent, text="LAT:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		lon2 = tk.Label(parent, text="LON:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		alt2 = tk.Label(parent, text="ALT:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		time2 = tk.Label(parent, text="TIME:", anchor="e", width=10, font=FONT, padx=3, pady=3)
		date2 = tk.Label(parent, text="DATE:", anchor="e", width=10, font=FONT, padx=3, pady=3)

		lat2.grid(row=0, column=0, sticky="ew")
		lon2.grid(row=1, column=0, sticky="ew")
		alt2.grid(row=2, column=0, sticky="ew")
		time2.grid(row=3, column=0, sticky="ew")
		date2.grid(row=4, column=0, sticky="ew")

		#setup GPS data panel
		self.lat = tk.Label(parent, text="          ", font=FONT, relief="groove", padx=3, pady=3)
		self.lon = tk.Label(parent, text="          ", font=FONT, relief="groove", padx=3, pady=3)
		self.alt = tk.Label(parent, text="          ", font=FONT, relief="groove", padx=3, pady=3)

		self.time = Clock(parent, self.gps_date, " UTC")
		self.time.configure(font=FONT, fg='blue', relief="groove", padx=3, pady=3)
		self.time.configure(text="          ")
	
		self.date = Clock(parent, self.gps_date, None, '%Y-%m-%d')
		self.date.configure(font=FONT, fg='blue', relief="groove", padx=3, pady=3)
		self.date.configure(text="          ")

		self.lat.grid(row=0, column=1, sticky="ew")
		self.lon.grid(row=1, column=1, sticky="ew")
		self.alt.grid(row=2, column=1, sticky="ew")
		self.time.grid(row=3, column=1, sticky="ew")
		self.date.grid(row=4, column=1, sticky="ew")


	def select_port(self):
		global app
		port = comPortDialog(self).show()
		if port == "None":
			self.port = None
			app.update_gps.configure(state=tk.DISABLED)
		else:
			self.port = port
			print("New port = {}".format(self.port))
			app.update_gps.configure(state=tk.NORMAL)

	def connect_gps(self):
		global app
		if self.gps_connected:
			self.gps.close()
			self.gps_connected = False
			app.change_serial.configure(state=tk.NORMAL)
		else:
			if self.port is not None and self.port != "None":
				app.change_serial.configure(state=tk.DISABLED)
				app.update_gps.configure(text="Disconnect GPS")
				self.update_gps_data()

	def update_gps_data(self):
		try:
			self.gps = Serial(port = self.port, timeout = 5)
			self.gps_connected = True
			print("Updating data from {}".format(self.port))

			loop = True
			iter = 1
			MAX_ITER = 25
 
			while loop:
				self.gps_sentence = self.gps.readline().decode("utf-8").rstrip()
				print("GPS DATA: {}".format(self.gps_sentence))
				for x in self.gps_sentence:
					self.gps_parser.update(x)
				loop = (self.gps_parser.valid == False or self.gps_parser.latitude == [0, 0.0, 'N'] or self.gps_parser.altitude == 0.0)
				if iter >= MAX_ITER:
					loop = False
				iter += 1

			if iter >= MAX_ITER:
				self.lat.configure(text = "  ** No Fix **  ")
				self.lon.configure(text = "  ** No Fix **  ")
				self.alt.configure(text = "  ** No Fix **  ")
				self.time.configure(text = "  ** No Fix **  ")
				self.date.configure(text = "  ** No Fix **  ")
				self.gps_valid = False
			else:
				self.gps_lat = self.gps_parser.latitude[0] + self.gps_parser.latitude[1]/60
				if self.gps_parser.latitude[2] == "S":
					self.gps_lat = -self.gps_lat
		
				self.gps_lon = self.gps_parser.longitude[0] + self.gps_parser.longitude[1]/60
				if self.gps_parser.longitude[2] == "W":
					self.gps_lon = -self.gps_lon

				self.gps_date = UTC.localize(datetime(self.gps_parser.date[2] + 2000, self.gps_parser.date[1], self.gps_parser.date[0],\
					self.gps_parser.timestamp[0], self.gps_parser.timestamp[1], int(self.gps_parser.timestamp[2])))

				self.gps_alt = self.gps_parser.altitude

				self.lat.configure(text="{:<+.4f} °".format(self.gps_lat))
				self.lon.configure(text="{:<+.4f} °".format(self.gps_lon))
				self.alt.configure(text="{:<+,.1f} m".format(int(self.gps_alt)))
				
				self.time.set(self.gps_date)
				self.date.set(self.gps_date)
				
				self.time.tick()
				self.date.tick('%Y-%m-%d')
				
				self.gps_valid = True
		except:
			raise


class DataFrame(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		
		global FONT
		WIDTH = 300
		HEIGHT = 200
		PAD = 3

		#######################################
		#testing variables
		SCP_LAT = 50.5555
		SCP_LON = -114.3014
		SCP_ALT = 1250.0
		SCP_DATE = datetime(2018, 9, 1, 23, 59, 23)
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
		self.scope_time.configure(font=FONT, fg='blue', relief="groove", padx=3, pady=3)
	
		self.scope_date = Clock(self.left_panel, SCP_DATE, None, '%Y-%m-%d')
		self.scope_date.configure(font=FONT, fg='blue', relief="groove", padx=3, pady=3)

		self.scope_lat.grid(row=0, column=1, sticky="ew")
		self.scope_lon.grid(row=1, column=1, sticky="ew")
		self.scope_alt.grid(row=2, column=1, sticky="ew")
		self.scope_time.grid(row=3, column=1, sticky="ew")
		self.scope_date.grid(row=4, column=1, sticky="ew")

		#create gps data panel
		app.gpsdata = GpsFrame(self.right_panel)

		#setup control panel
		self.btmFrame.grid_rowconfigure(1, weight=1)
		self.btmFrame.grid_columnconfigure(1, weight=1)

		app.update_gps = tk.Button(self.btmFrame, text="Get GPS Data", command=app.gpsdata.connect_gps, state=tk.DISABLED)
		app.update_gps.grid(row=0,column=1, sticky="ne")

		app.change_serial = tk.Button(self.btmFrame, text="Config Serial", command=app.gpsdata.select_port)
		app.change_serial.grid(row=0,column=0, sticky="ne")

if __name__ == "__main__":
	global app
	global watcherThread
	app = tk.Tk()
	app.protocol("WM_DELETE_WINDOW", exit_event)
	app.stop = False
	app.data = DataFrame(app)
	app.data.pack()

	watcherThread = Worker("clock_watcher")
	watcherThread.start()
	app.mainloop()