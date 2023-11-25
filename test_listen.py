import speech_recognition as sr
from gpiozero import Button
import sounddevice

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        print(r.recognize_google(audio))
    except sr.RequestError as e:
        print(f'error {e}')
        
  
if __name__ == '__main__':
    listen()
