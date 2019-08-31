from micropyGPS import MicropyGPS
from serial import Serial

PORT = 'COM4'
ser = Serial(PORT)

myGPS = MicropyGPS()
go = True

while go==True:
	ser_bytes = ser.readline().decode("utf-8").rstrip()
	print("RAW GPS Data:  {}".format(ser_bytes))
	for x in ser_bytes:
		myGPS.update(x)

	print("Latitude  = {}".format(myGPS.latitude))
	print("Longitude = {}".format(myGPS.longitude))
	print("Altitude  = {}".format(myGPS.altitude))
	print("UTC Time  = {}".format(myGPS.timestamp))
	print("UTC Date  = {}".format(myGPS.date))
	print("\n")

	if myGPS.valid == True:
		if myGPS.altitude != 0.0 and myGPS.latitude != [0, 0.0, 'N']:
			go = False