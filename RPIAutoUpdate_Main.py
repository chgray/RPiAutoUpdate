from RPIAutoUpdate import *
from WifiCreds import *
# https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython

print("Version: 0.3")
print("")
print("Usage:")
print("To get to python() flash RPI_PICO_W-20241025-v1.24.0.uf2 - it wont erase files but will go to python")


creds = WifiCreds()

# Create (but dont init) uploaders
downloader = RPIAutoUpdateFileDownloaderWifi()
cu = RPIAutoUpdateUpdater(downloader)

#
# Print useful update configurations
#
print("")
print("")
print("          UPDATE_ON_BOOT=%d" % creds.UpdateOnBoot())
print("     UPDATE_IS_REQUESTED=%d" % cu.IsUpdateRequested())
print("         UPDATE_IS_READY=%d" % cu.IsUpdateReady())

#
# On PicoW init wifi
#
if True == creds.UpdateOnBoot() or cu.IsUpdateRequested():
    print("Doing Update over WiFi")
    try:
        if hasattr(network, "WLAN"):
            print("Initing WiFi")
            downloader.InitWifi()
            print("Connecting WiFi")
            downloader.Connect()
        else:
            print("NOT WIFI DEVICE!!!! - EXITING")
            exit(1)

        cu.Update()

        if True == cu.IsUpdateReady():
            print("REBOOTING! - update is ready")
            sleep(3)
            machine.reset()

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


if True == cu.IsUpdateReady():
    cu.FinishUpdate()
    print("REBOOTING! - update is ready")
    sleep(3)
    machine.reset()

if True == cu.IsUpdateReady():
    print("REBOOTING! - update is still requested")
    sleep(3)
    machine.reset()


if creds.ConnectWifiForApp():
    downloader.InitWifi()
    downloader.Connect()


print("Loading Main Program")
from RPIAutoUpdate_application import *
updatedMain = RPIAutoUpdate_application()
print("Loading Main Program")
updatedMain.Main()


print("...........We're exiting............")