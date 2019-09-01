from micropyGPS import MicropyGPS
from serial import Serial
import win32com.client
from pytz import UTC
from datetime import datetime


x = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
x.DeviceType = "Telescope"
device = x.Choose(None)
tel = win32com.client.Dispatch(device)
tel.Connected = True

# Establish GPS
GPS_PORT = 'COM4'
gps = Serial(GPS_PORT)

myGPS = MicropyGPS()

# Retrieve GPS position data
while myGPS.valid == False or myGPS.latitude == [0, 0.0, 'N']:
	gps_data = gps.readline().decode("utf-8").rstrip()
	for x in gps_data:
		myGPS.update(x)

# Set Telescope Date/Time
d = UTC.localize(datetime(myGPS.date[0], myGPS.date[1], myGPS.date[2],\
 myGPS.timestamp[0], myGPS.timestamp[1], int(myGPS.timestamp[2])))
tel.UTCDate = d

# Set Telescope Position, Altitude
gps_lat = myGPS.latitude[0] + myGPS.latitude[1]/60
if myGPS.latitude[2] == "S":
	gps_lat = -gps_lat

gps_lon = myGPS.longitude[0] + myGPS.longitude[1]/60
if myGPS.longitude[2] == "W":
	gps_lon = -gps_lon

tel.SiteLatitude = gps_lat
tel.SiteLongitude = gps_lon
tel.SiteElevation = myGPS.altitude

print("+-------------------------------------------------+")
print("| Site Latitude          |  {:<+9.4f}             |".format(tel.SiteLatitude))
print("| Site Longitude         |  {:<+9.4f}             |".format(tel.SiteLongitude))
print("| Site Elevation         |  {:<+7.2f}               |".format(tel.SiteElevation))
print("| Scope Date             |  {:%Y/%m/%d}            |".format(tel.UTCDate))
print("| Scope Time             |  {:%H:%M:%S}              |".format(tel.UTCDate))
print("+-------------------------------------------------+")

tel.Connected = False
