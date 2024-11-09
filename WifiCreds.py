import machine

class WifiCreds:

    def __init__(self):
        print("GOOD: Opened WiFi Credential file from local filesystem")

    def DeviceFunction(self):
        return 'https://raw.githubusercontent.com/chgray/OpenCoffee/user/chgray/se2/WifiRelay.json'

    def SSID(self):
        return "Guest"

    def PWD(self):
        return 'guest123'
