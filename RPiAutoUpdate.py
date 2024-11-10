import network, os
import urequests
import ustruct
import time
import io
import hashlib
import binascii
import time
import machine
import ujson

from WifiCreds import *
from machine import UART
from machine import Pin, Timer
from machine import Pin, Timer
from time import sleep
from machine import Pin

# https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython


fixedLed = Pin("LED", Pin.OUT)
#wdt = WDT(timeout=8000) #timeout is in ms
timer = Timer()

fixedLed.value(1)
sleep(1)
fixedLed.value(0)



def callback(data):
    print("INTERRUPT")
    print(data)

startTime = time.ticks_ms()

def fileExists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False

def pokeWatchDog():
    fixedLed.toggle()
    #global wdt
    #global fixedLed
    #global startTime

    #if startTime + (6 * 60 *  1000) < time.ticks_ms():
    #    print("RESETING")
    #    machine.reset()

    #led = Pin("LED", Pin.OUT)
    #fixedLed.value(0)
    #sleep(1)
    #print("WatchDog Poke")
    #fixedLed.value(1)
    #wdt.feed() #resets countdown
    #fixedLed.toggle()

def pokeWatchDogTimer(t):
    #print("Watchdog Timer")
    #fixedLed.toggle()
    pokeWatchDog()


#print("Initing Timer")
#timer.init(mode=Timer.PERIODIC, period=200, callback=pokeWatchDogTimer)
#print("...timer inited")


#
# Read update file
#
class RPiAutoUpdateUpdater(object):

    def __init__(self, downloader):
        self.downloader = downloader

    def Update(self):
        creds = WifiCreds()
        print("UPDATER: Device Update URL: %s" % creds.DeviceFunction())

        # Retrieve our high water config file
        targetConfig = self.downloader.LoadContent(creds.DeviceFunction())
        targetConfigJson = ujson.load(io.StringIO(targetConfig.Content()))

        print(targetConfig.Content())

        print("UPDATER: Device Function : %s" % targetConfigJson["DeviceFunction"])

        print("")
        print("")
        print("Required Files: -------------------------------------------------------")
        for key, value in enumerate(targetConfigJson['Files']):
            print ("    * %s with hash %s" % (value["FileName"], value["Hash"]))

        print("")
        print("")
        print("Updating Files: -------------------------------------------------------")
        for key, value in enumerate(targetConfigJson['Files']):
            print ("    Checking %s for updates" % value["FileName"])
            try:
                localFile = self.downloader.LoadFile(value["FileName"])
                needUpdate = False

                if localFile == None:
                    print("    * File (%s) DOES NOT EXIST in local filesystem;  forcing update" % localFile)
                    needUpdate = True
                else:
                    if localFile.Hash() != value["Hash"]:
                        print("    * File (%s) DOES EXIST locally, but hashs differ (remote=%s, local=%s)" % (localFile, value["Hash"], localFile.Hash()))
                        needUpdate = True
                    else:
                        print("    * File (%s) DOES EXIST locally, hashs the same - no update required)" % (localFile))

                if needUpdate:
                    content = self.downloader.LoadContent(value["URL"])

                    if content.Hash() == value["Hash"]:
                        print ("    * FILE HASH IS CORRECT!")
                    else:
                        print ("    * CORRUPTED FILE HASH expected=%s vs. actual=%s" % (content.Hash(), value["Hash"]))
                        needUpdate = False

                if needUpdate:
                    print("")
                    print("    Performing Update...")
                    with open(value["FileName"] + ".temp", "wb") as    FILE:
                        print("    Writing temp file")
                        file.write(content.Content())

                    if localFile != None:
                        print("   Removing original file")
                        os.remove(value["FileName"])

                    print("    Perform rename")
                    os.rename(value["FileName"] + ".temp", value["FileName"])

                    print("    SUCCESS: %s updated!" % value["FileName"])


            except OSError as e:
                print("OSERROR() - download - reseting!")
                #machine.reset()



class ChecksumContent(object):

    def __init__(self, content):
        #print("ChecksumContent : %d" % len(content))
        self.shaHash = hashlib.sha256(content)
        self.hexHash = binascii.hexlify(self.shaHash.digest())
        self.hexHash = self.hexHash.decode('utf-8')
        self.content = content

        #print(self.Hash())
        #print("HexHash %s" % self.hexHash)

    def Content(self):
        return self.content

    def Hash(self):
        return self.hexHash

class RPiAutoUpdateFileDownloader(object):
    def __init__(self):
        print("   FILE: OpenRPiAutoUpdate Downloader Initialized")

    def LoadFile(self, location):
        #print("Getting %s from FILESYSTEM" % location)

        if fileExists(location) == False:
            return None

        with open(location, 'rb') as f:
            ret = ChecksumContent(f.read())
            return ret

    def LoadContent(self, location):
        print("   FILE: Opening %s from disk" % location)

        if fileExists(location) == False:
            return None

        with open(location, 'rb') as f:
            ret = ChecksumContent(f.read())
            return ret

class RPiAutoUpdateFileDownloaderWifi(RPiAutoUpdateFileDownloader):
    def __init__(self):
        super().__init__()
        print("   WIFI: OpenRPiAutoUpdate Downloader Initialized")

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)

        fixedLed.value(1)
        sleep(1)
        fixedLed.value(0)

    def Connect(self):
        creds = WifiCreds()
        self.m_ssid = creds.SSID()
        self.m_password = creds.PWD()

        # scanlist = self.wlan.scan()
        # for result in scanlist:
        #     ssid, bssid, channel, RSSI, authmode, hidden = result
        #     print("     %s == %s,  authmode=%d" % (ssid, ubinascii.hexlify(bssid), authmode))

        print("   WIFI: Connecting to %s with password %s" % (self.m_ssid, self.m_password))

        self.wlan.active(True)
        fixedLed.value(1)
        sleep(3)
        self.wlan.connect(self.m_ssid, self.m_password)

        while self.wlan.isconnected() == False:
            print('   WIFI: waiting for connection...  Status=%d, connected=%d' % (self.wlan.status(), self.wlan.isconnected()))
            sleep(1)

        if self.wlan.isconnected():
            status = self.wlan.ifconfig()
            print('   WIFI: connected to %s network, ip=%s' % (self.m_ssid, status[0]))

        else:
            print('   WIFI: network connection failed')
            machine.reset()

    def LoadContent(self, location):
        print("   WIFI: Downloading file %s" % location)
        response = urequests.get(location)
        hash_object = hashlib.sha256(response.text)
        hex_dig = binascii.hexlify(hash_object.digest())
        ret = ChecksumContent(response.text)
        return ret



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

print("Blinking LEDs for a bit")
sleep(1)
print("Bye!! - xyz")
sleep(5)
machine.reset()