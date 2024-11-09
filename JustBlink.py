from machine import Pin, Timer
from time import sleep

print("Just Blink Example")

led = Pin("LED", Pin.OUT)
timer = Timer()

def blink(timer):
    print("Timer Tick")
    led.toggle()

timer.init(freq=10, mode=Timer.PERIODIC, callback=blink)

print("bye")
sleep(60)
print("done")