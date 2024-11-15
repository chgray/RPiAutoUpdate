from RPiAutoUpdate import *
from WifiCreds import *
# https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython

print("Version: 0.1")
print("")
print("Usage:")
print("   0. to get to python() flash RPI_PICO_W-20241025-v1.24.0.uf2 - it wont erase files but will go to python")
print("   1. follow instructions for wifi credentials and default configuration")
print("   2. copy this file as main.py' -- eg: ampy put RPiAutoUpdate_Main.py main.py")

creds = WifiCreds()

print("Creds %d" % creds.Do_Not_Use_Network())
#
# On PicoW init wifi
#
if False == creds.Do_Not_Use_Network():
    try:
        if hasattr(network, "WLAN"):
            print("WIFI")
            downloader = RPiAutoUpdateFileDownloaderWifi()
            print("Initing WiFi")
            downloader.InitWifi()
            print("Connecting WiFi")
            downloader.Connect()
        else:
            print("NOT WIFI DEVICE!!!! - EXITING")
            exit(1)

        cu = RPiAutoUpdateUpdater(downloader)
        cu.Update()

    except OSError as e:
            print('Closing Up...')
            print("OSERROR() - reseting!")
            #machine.reset()

    except KeyboardInterrupt as e:
        print('Keyboard-Closing Up...')
        print("KEYBOARDINTERRUPT() - reseting!")
        #machine.reset()

    except Exception as e:
        print('Closing Up...')
        print("EXCEPTION() - reseting!")
        machine.reset()


print("Loading Main Program")
from RPiAutoUpdate_application import *
updatedMain = RPiAutoUpdate_application()
print("Loading Main Program")
updatedMain.Main()