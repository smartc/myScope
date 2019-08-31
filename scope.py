import win32com.client
from pywintypes import Time as pyTime
from time import gmtime

#scopeName = "ASCOM.Celestron.Telescope"

x = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
x.DeviceType = "Telescope"
d = x.Choose(None)
print( d )
tel = win32com.client.Dispatch(d)

tel.Connected = True
#tel.Tracking = True
print(tel.SiteLatitude)
print(tel.SiteLongitude)
print(tel.UTCDate)

tel.UTCDate = pyTime(gmtime())
print(tel.UTCDate)

#tel.SlewToCoordinates(12.34, 86.7)
tel.Connected = False