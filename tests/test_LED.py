import speech_recognition as sr
from gpiozero import Button, LED
import apa102
import sounddevice

def listen():
    
    driver = apa102.APA102(num_led=12)
    power = LED(5)
    power.on()
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # ambient adjustment causes longer delay
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        
        for i in range(12):
            driver.set_pixel(i, 0, 0, 255)
        driver.show()
        
        audio = r.listen(source)

    try:
        print('Recognizing...')
        print(r.recognize_google(audio))
    except sr.RequestError as e:
        print(f'error {e}')
        
  
if __name__ == '__main__':
    listen()
