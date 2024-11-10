from RPiAutoUpdate import *
# https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython

print("Hello World")

#
# On PicoW init wifi
#
try:
    if hasattr(network, "WLAN"):
        print("WIFI")
        downloader = RPiAutoUpdateFileDownloaderWifi()
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
from RPiAutoUpdate_main import *
updatedMain = RPiAutoUpdate_main()
print("Loading Main Program")
updatedMain.Main()