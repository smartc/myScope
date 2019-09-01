from micropyGPS import MicropyGPS
from serial import Serial
from serial_tools import serial_ports
import win32com.client
from pytz import UTC
from datetime import datetime
from sys import exit

telescope = None
gpsData = None

GPS_TIME = 0
PC_TIME = 1
TIMEOUT = 10

def connectScope():
	x = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
	x.DeviceType = "Telescope"
	device = x.Choose(None)
	try:
		tel = win32com.client.Dispatch(device)
		tel.Connected = True
		return tel
	except:
		print("")
		print("*** Error opening telescope ***")
		print("")
		exit(1)

def connectGPS():
	ports = serial_ports()
	gps = None
	while gps is None:
		print("+------------------------------------+")
		print("| Available serial ports             |")
		print("+------------------------------------+")
		n=1
		for p in ports:
			print("| {:>2}) {:10}                     +".format(n,p))
			n =n + 1
		print("+------------------------------------+")
		port_num = int(input("Select GPS Port #:"))-1
		try:
			GPS_PORT = ports[port_num]
			gps = Serial(GPS_PORT, timeout=TIMEOUT)
		except IndexError:
			print("*** Error - invalid selection ***")
			continue
		except:
			print("*** Error opening com port {} ***".format(GPS_PORT))
			exit(1)
	return gps


def getGPSData(gps, MAX_ITER = 20):
	myGPS = MicropyGPS()
	iter_n = 0
	loop = True

	while loop: 
		gps_data = gps.readline().decode("utf-8").rstrip()
		for x in gps_data:
			myGPS.update(x)
		loop = (myGPS.valid == False or myGPS.latitude == [0, 0.0, 'N'] or myGPS.altitude == 0.0)
		iter_n = iter_n + 1
		if iter_n >= MAX_ITER:
			if myGPS.valid == False:
				print("")
				print("*** No GPS Fix ***")
				print("")
				exit(1)
			else:
				print("")
				print("*** Caution: Some GPS data may be invalid ***")
				print("***          Please validate settings     ***")
				print("")
				loop = False
	return myGPS

def setScopeTime(mode = GPS_TIME):
	if mode == GPS_TIME:
		d = UTC.localize(datetime(gpsData.date[2], gpsData.date[1], gpsData.date[0],\
			gpsData.timestamp[0], gpsData.timestamp[1], int(gpsData.timestamp[2])))
	else:
		d = UTC.localize(datetime.now())

	telescope.UTCDate = d

def setScopePosition():
	gps_lat = gpsData.latitude[0] + gpsData.latitude[1]/60
	if gpsData.latitude[2] == "S":
		gps_lat = -gps_lat

	gps_lon = gpsData.longitude[0] + gpsData.longitude[1]/60
	if gpsData.longitude[2] == "W":
		gps_lon = -gps_lon

	telescope.SiteLatitude = gps_lat
	telescope.SiteLongitude = gps_lon

def setScopeElevation():
	telescope.SiteElevation = gpsData.altitude


if __name__ == "__main__":

	telescope = connectScope()
	gpsDevice = connectGPS()
	gpsData = getGPSData(gpsDevice)

	setScopeTime()
	setScopePosition()
	setScopeElevation()

	print("")
	print("+-------------------------------------------------+")
	print("| New Telescope Position Data                     |")
	print("+-------------------------------------------------+")
	print("| Site Latitude          |  {:<+10.4f}            |".format(telescope.SiteLatitude))
	print("| Site Longitude         |  {:<+10.4f}            |".format(telescope.SiteLongitude))
	print("| Site Elevation (m)     |  {:<+10.2f}            |".format(telescope.SiteElevation))
	print("| Scope Date             |  {:%Y/%m/%d}            |".format(telescope.UTCDate))
	print("| Scope Time             |  {:%H:%M:%S}              |".format(telescope.UTCDate))
	print("+-------------------------------------------------+")

	telescope.Connected = False