from micropyGPS import MicropyGPS
from serial import Serial
import win32com.client

GPS_PORT = 'COM4'
gps = Serial(GPS_PORT)

myGPS = MicropyGPS()
go = True

while go==True:
	gps_data = gps.readline().decode("utf-8").rstrip()
	print("RAW GPS Data:  {}".format(gps_data))
	for x in gps_data:
		myGPS.update(x)

	print("Latitude  = {}".format(myGPS.latitude))
	print("Longitude = {}".format(myGPS.longitude))
	print("Altitude  = {}".format(myGPS.altitude))
	print("UTC Time  = {}".format(myGPS.timestamp))
	print("UTC Date  = {}".format(myGPS.date))
	print("\n")

	if myGPS.valid == True and myGPS.latitude != [0, 0.0, 'N']:
			go = False

gps_lat = myGPS.latitude[0] + myGPS.latitude[1]/60
if myGPS.latitude[2] == "S":
	gps_lat = -gps_lat

gps_lon = myGPS.longitude[0] + myGPS.longitude[1]/60
if myGPS.longitude[2] == "W":
	gps_lon = -gps_lon

print("Latitude DD.DDDD  = {:.4f}".format(gps_lat))
print("Longitude DD.DDDD = {:.4f}".format(gps_lon))


x = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
x.DeviceType = "Telescope"
device = x.Choose(None)
tel = win32com.client.Dispatch(device)
tel.Connected = True

print(tel.SiteLatitude)
print(tel.SiteLongitude)

tel.SiteLatitude = gps_lat
tel.SiteLongitude = gps_lon

print(tel.SiteLatitude)
print(tel.SiteLongitude)