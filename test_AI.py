import speech_recognition as sr
from gpiozero import Button, LED
import apa102
import sounddevice
from openai import OpenAI
from elevenlabs import generate, play

class Jarvis():

    def __init__(self):
        self.client = OpenAI()
        
#     def init_leds(self):
#         power = LED(5)
#         power.on()

    def listen(self):

#         self.init_leds()
        
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
            driver.clear_strip()

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
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Answer as if you are J.A.R.V.I.S. from Iron Man."},
                    {"role": "user", "content": text}])
            
            resp_str = response.choices[0].message.content
            
            print(resp_str)
            return resp_str

        else:
            print('No text recognized')
            return None

    def play(self, response):

        audio = generate(
            text=response,
            voice="Stanley",
            model="eleven_monolingual_v1"
            )

        play(audio)


    def run(self):

        text = self.listen()
        response = self.request(text)
        self.play(response)
    
  
if __name__ == '__main__':

    jv = Jarvis()
    jv.run()