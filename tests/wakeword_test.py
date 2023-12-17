import pvporcupine
from pvrecorder import PvRecorder
import os

key = os.getenv('PICOVOICE_API_KEY')
words = ['jarvis']

porcupine = pvporcupine.create(access_key=key, keywords=words)
recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

try:
    recorder.start()
    
    while True:
        idx = porcupine.process(recorder.read())
        
        if idx >= 0:
            print(f'Detected {words[idx]}')
            
except KeyboardInterrupt:
    recorder.stop()
finally:
    porcupine.delete()