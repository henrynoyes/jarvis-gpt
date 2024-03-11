import pvporcupine
from pvrecorder import PvRecorder
import os
from main import Jarvis, Shutdown
from pygame import mixer
from time import sleep

jv = Jarvis()

porcupine = pvporcupine.create(access_key=os.getenv('PICOVOICE_API_KEY'), keywords=['jarvis'])
recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

mixer.init()
mixer.music.load('./media/welcome_back.mp3')

try:
    mixer.music.play()
        
    recorder.start()
    print('JARVIS activated')
    while True:
        idx = porcupine.process(recorder.read())
        
        if idx >= 0:
            jv.run()

except Shutdown:
    recorder.stop()
    mixer.music.load('./media/shutting_down.mp3')
    mixer.music.play()
    sleep(2)

except KeyboardInterrupt:
    recorder.stop()

finally:
    porcupine.delete()