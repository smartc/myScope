from serial_tools import serial_ports

import tkinter as tk

class comPortDialog(tk.Toplevel):
	def __init__(self, parent):
		tk.Toplevel.__init__(self, parent)

		self.coms = serial_ports()

		self.selected_port = tk.StringVar()
		if parent.port is None:
			self.selected_port.set(None)
		else:
			self.selected_port.set(parent.port)

		self.label = tk.Label(self, text="Select COM Port:")
		self.options = tk.OptionMenu(self, self.selected_port, *self.coms)
		self.ok_button = tk.Button(self, text="OK", command=self.on_ok)

		self.label.pack(side="top", fill="x")
		self.options.pack(side="top", fill="x")
		self.ok_button.pack(side="right")

	def on_ok(self, event=None):
		self.destroy()

	def show(self):
		self.wm_deiconify()
		self.options.focus_force()
		self.wait_window()
		return self.selected_port.get()

class Primary(tk.Frame):

	def __init__(self, parent):
		tk.Frame.__init__(self,parent)
		self.port = None
		self.button = tk.Button(self, text="Select GPS", command=self.getGPS)
		self.label = tk.Label(self, text="", width=20)
		self.button.pack(padx=4, pady=4)
		self.label.pack(side="bottom", fill="both", expand=True)

	def getGPS(self):
		self.port = comPortDialog(self).show()
		self.label.configure(text="COM PORT: {}".format(self.port))


if __name__=="__main__":
	root = tk.Tk()
	root.wm_geometry("400x200")
	Example(root).pack(fill="both", expand=True)
	root.mainloop()
