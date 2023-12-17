import pvporcupine
from pvrecorder import PvRecorder
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from main import Jarvis
from pygame import mixer
import apa102
from gpiozero import LED
import time

jv = Jarvis()

porcupine = pvporcupine.create(access_key=os.getenv('PICOVOICE_API_KEY'), keywords=['jarvis'])
recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

mixer.init()
mixer.music.load('./media/welcome_back.mp3')

try:
    mixer.music.play()
    
    driver = apa102.APA102(num_led=12)
    power = LED(5)
    power.on()
    
    for i in range(12):
        driver.set_pixel(i, 0, 255, 255)
        driver.show()
        time.sleep(0.66)    
    driver.clear_strip()
    driver.cleanup()
    power.off()
    power.close()
    
    recorder.start()
    print('JARVIS activated')
    while True:
        idx = porcupine.process(recorder.read())
        
        if idx >= 0:
            jv.run()
            
except KeyboardInterrupt:
    recorder.stop()
finally:
    porcupine.delete()