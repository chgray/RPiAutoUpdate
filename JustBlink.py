from machine import Pin, Timer
from time import sleep


class RPiAutoUpdate_application:

    def __init__(self):
        print("JustBlink Initing!")

    def Main(self):
        print("JustBlink Main!")
        led = Pin("LED", Pin.OUT)
        timer = Timer()

        def blink(timer):
            print("Timer Tick")
            led.toggle()

        timer.init(freq=10, mode=Timer.PERIODIC, callback=blink)

        print("bye")
        sleep(20)
        print("done")