from RPiAutoUpdate import *
# https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython

print("Usage:")
print("   1. run this tool - it'll tell you what the hashs for all files in storage")

downloader = RPiAutoUpdateFileDownloaderWifi()

print("")
print("")
print("Discovered Files: -------------------------------------------------")
for file in os.listdir('/'):
    print(file)


for file in os.listdir('/'):
    localFile = downloader.LoadFile(file)
    print("%s : %s" % (localFile.Hash(), file))


