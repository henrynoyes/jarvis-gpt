from main import Jarvis, Shutdown
import RPi.GPIO as GPIO
from pygame import mixer
from time import sleep
from collections import deque

class Buffer(deque):
    def __init__(self, maxlen=None):
        super().__init__([0] * maxlen, maxlen=maxlen)

    def zeros(self):
        self.extend([0] * self.maxlen)

jv = Jarvis()

pin = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

buf = Buffer(maxlen=10)

mixer.init()
mixer.music.load('./media/welcome_back.mp3')

try:
    mixer.music.play()
    
    jv.startup()

    print('JARVIS activated')

    while True:
        state = GPIO.input(pin)
        buf.append(state)

        if all(buf):
            jv.run()
        
        sleep(0.05)
            

except Shutdown:
    mixer.music.load('./media/shutting_down.mp3')
    mixer.music.play()
    sleep(2)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
