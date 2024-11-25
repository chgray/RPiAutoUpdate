import machine

class WifiCreds:

    def __init__(self):
        print("Opened WiFi Credential file from local filesystem")

    def UpdateOnBoot(self):
        return True

    def ConnectWifiForApp(self):
        return False

    def DeviceFunction(self):
        return 'https://raw.githubusercontent.com/chgray/RPiAutoUpdate/refs/heads/user/chgray/iterating/JustBlink.json'

    def SSID(self):
        return "Guest"

    def PWD(self):
        print("PWD....")
        return 'guest123'
