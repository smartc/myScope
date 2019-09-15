from micropyGPS import MicropyGPS
from serial import Serial
from serial_tools import serial_ports
#import win32com.client
from pytz import UTC
from datetime import datetime
from sys import exit


#x = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
#x.DeviceType = "Telescope"
#device = x.Choose(None)
#tel = win32com.client.Dispatch(device)
#try:
#	tel.Connected = True
#except:
#	print("")
#	print("*** Error opening telescope ***")
#	print("")
#	exit(1)

# Connect to GPS
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
		gps = Serial(GPS_PORT)
	except IndexError:
		print("*** Error - invalid selection ***")
		continue
	except:
		print("*** Error opening com port {} ***".format(GPS_PORT))
		tel.Connected = False
		exit(1)

myGPS = MicropyGPS()

# Retrieve GPS position data
#  Altitude is not available in all NMEA sentences and is not returned by BT GPS app
#  Intent of iter_n variable is to limit number of iterations while ensuring all variables are set
iter_n = 0
MAX_ITER = 50
loop = True
while loop: 
	gps_data = gps.readline().decode("utf-8").rstrip()
	print("GPS DATA: {}".format(gps_data))
	for x in gps_data:
		myGPS.update(x)
	loop = (myGPS.valid == False or myGPS.latitude == [0, 0.0, 'N'] or myGPS.altitude == 0.0)
	iter_n = iter_n + 1
	if iter_n >= MAX_ITER:
		if myGPS.valid == False:
			print("")
			print("*** No GPS Fix ***")
			print("")
#			tel.Connected = False
			exit(1)
		else:
			print("")
			print("*** Caution: Some GPS data may be invalid ***")
			print("***          Please validate settings     ***")
			print("")
			loop = False

# Set Telescope Date/Time
d = UTC.localize(datetime(myGPS.date[2], myGPS.date[1], myGPS.date[0],\
 myGPS.timestamp[0], myGPS.timestamp[1], int(myGPS.timestamp[2])))
#tel.UTCDate = d

# Set Telescope Position, Altitude
gps_lat = myGPS.latitude[0] + myGPS.latitude[1]/60
if myGPS.latitude[2] == "S":
	gps_lat = -gps_lat

gps_lon = myGPS.longitude[0] + myGPS.longitude[1]/60
if myGPS.longitude[2] == "W":
	gps_lon = -gps_lon

#tel.SiteLatitude = gps_lat
#tel.SiteLongitude = gps_lon
#tel.SiteElevation = myGPS.altitude

print("")
print("+-------------------------------------------------+")
print("| New Telescope Position Data                     |")
print("+-------------------------------------------------+")
print("| Site Latitude          |  {:<+10.4f}            |".format(gps_lat))
print("| Site Longitude         |  {:<+10.4f}            |".format(gps_lon))
print("| Site Elevation (m)     |  {:<+10.2f}            |".format(myGPS.altitude))
print("| Scope Date             |  {:%Y/%m/%d}            |".format(d))
print("| Scope Time             |  {:%H:%M:%S}              |".format(d))
print("+-------------------------------------------------+")

#tel.Connected = False