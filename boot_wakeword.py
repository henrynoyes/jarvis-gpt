import pvporcupine
from pvrecorder import PvRecorder
import os
from main import Jarvis

jv = Jarvis()
porcupine = pvporcupine.create(access_key=os.getenv('PICOVOICE_API_KEY'), keywords=['jarvis'])
recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

try:
    recorder.start()
    
    while True:
        idx = porcupine.process(recorder.read())
        
        if idx >= 0:
            jv.run()
            
except KeyboardInterrupt:
    recorder.stop()
finally:
    porcupine.delete()