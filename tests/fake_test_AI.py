import speech_recognition as sr
from gpiozero import Button, LED
import apa102
import sounddevice
from openai import OpenAI

class Jarvis():

    def __init__(self):
        self.client = OpenAI()

    def init_leds(self):
        self.driver = apa102.APA102(num_led=12)
        power = LED(5)
        power.on()

    def listen(self):

        self.init_leds()

        r = sr.Recognizer()
        with sr.Microphone() as source:
            # ambient adjustment causes longer delay
            r.adjust_for_ambient_noise(source)
            print("Listening...")
        
            for i in range(12):
                self.driver.set_pixel(i, 0, 0, 255)
            self.driver.show()
            
            audio = r.listen(source)

        try:
            print('Recognizing...')
            text = r.recognize_google(audio)
            print(text)
            return text

        except sr.RequestError as e:
            print(f'error {e}')
            return None
        
    def request(self, text):

        if text:
            print('Responding...')
            # response = self.client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": "You are the assistant J.A.R.V.I.S. from Iron Man."},
            #         {"role": "user", "content": text}])
            
            # print(response.choices[0].message)
            print('fake response')

        else:
            print('No text recognized')

    def run(self):

        text = self.listen()
        self.request(text)
    
  
if __name__ == '__main__':

    jv = Jarvis()
    jv.run()