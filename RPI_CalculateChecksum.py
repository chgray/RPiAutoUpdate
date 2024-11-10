from RPiAutoUpdate import *
# https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython

print("Usage:")
print("   1. copy file you wish to hash as 'toHash' -- eg: ampy put foo.py toHash")
print("   2. run ampy,  eg: ampy run RPI_CalculateChecksum.py")

#
# On PicoW init wifi
#
try:

    if hasattr(network, "WLAN"):
        print("Initing update helper")
        downloader = RPiAutoUpdateFileDownloaderWifi()
        print("Loading File toHash")
        hash = downloader.LoadFile("toHash")

        if hash == None:
            print("ERROR: couldnt load toHash")
        else:
            print("Hash: %s" % (hash.Hash()))
    else:
        print("NOT WIFI DEVICE!!!! - EXITING")
        exit(1)

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

