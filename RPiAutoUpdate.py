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
        print("   UPDATER: RPiAutoUpdate Updater Version 1.0")
        self.downloader = downloader

    def Update(self):
        print("")
        print("")
        print("Downloading Defice Function Config : ----------------------------")
        creds = WifiCreds()
        print("UPDATER: Device Update URL: %s" % creds.DeviceFunction())

        # Retrieve our high water config file
        targetConfig = self.downloader.LoadContent(creds.DeviceFunction())
        print("UPDATER: Downloaded config file %s" % targetConfig.Content())

        targetConfigJson = ujson.load(io.StringIO(targetConfig.Content()))

        print("UPDATER: Device Function : %s" % targetConfigJson["DeviceFunction"])

        print("")
        print("")
        print("Required Files: -------------------------------------------------")
        for key, value in enumerate(targetConfigJson['Files']):
            print ("    * %s with hash %s" % (value["FileName"], value["Hash"]))

        print("")
        print("")
        print("Updating Files: -------------------------------------------------")
        for key, value in enumerate(targetConfigJson['Files']):
            print ("    Checking %s for updates" % value["FileName"])
            try:
                localFile = self.downloader.LoadFile(value["FileName"])
                needUpdate = False

                if localFile == None:
                    print("    * File (%s) DOES NOT EXIST in local filesystem;  forcing update" % value["FileName"])
                    needUpdate = True
                else:
                    if localFile.Hash() != value["Hash"]:
                        print("    * File (%s) DOES EXIST locally, but hashs differ (remote=%s, local=%s)" % (value["FileName"], value["Hash"], localFile.Hash()))
                        needUpdate = True
                    else:
                        print("    * File (%s) DOES EXIST locally, hashs the same (remote=%s, local=%s) - no update required)" % (value["FileName"], value["Hash"], localFile.Hash()))


                #
                # If we need to update, download the file and write it to the filesystem
                #    if the remote hash doesnt match our calculated hash, then we have a problem, skip the file
                #
                if needUpdate:
                    print("")
                    print("    * Downloading remote file (%s)" % value["FileName"])
                    content = self.downloader.LoadContent(value["URL"])

                    if content.Hash() == value["Hash"]:
                        print ("    * FILE HASH IS CORRECT!")
                    else:
                        print ("    * CORRUPTED FILE HASH expected=%s vs. actual=%s" % (content.Hash(), value["Hash"]))
                        needUpdate = False

                #
                # If we're here, we have the updated file in memory, write it to disk
                #
                if needUpdate:
                    print("    * Writing file to disk as %s.temp" % value["FileName"])

                    with open(value["FileName"] + ".temp", "wb") as file:
                        file.write(content.Content())

                    if localFile != None:
                        print("    * Deleting file, if it exists")
                        os.remove(value["FileName"])

                    print("    * Perform rename %s -> %s" % (value["FileName"] + ".temp", value["FileName"]))
                    os.rename(value["FileName"] + ".temp", value["FileName"])

                    print("    * SUCCESS: %s updated!" % value["FileName"])


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
        print("   FILE: RPiAutoUpdate Downloader Initialized")

    def LoadFile(self, location):
        print("Getting %s from FILESYSTEM" % location)

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
        print("   WIFI: RPiAutoUpdate Downloader Initializing")


    def InitWifi(self):
        print("   WIFI: RPiAutoUpdate Downloader Initializing Wifi")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)

        fixedLed.value(1)
        sleep(1)
        fixedLed.value(0)
        print("   WIFI: RPiAutoUpdate Downloader Initialized Wifi")


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

