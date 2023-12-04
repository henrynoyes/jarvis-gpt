import speech_recognition as sr
from gpiozero import Button, LED
import apa102
import sounddevice
from openai import OpenAI
from elevenlabs import generate, stream

class Jarvis():

    def __init__(self):
        self.client = OpenAI()

    def listen(self):

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
        
        driver = apa102.APA102(num_led=12)
        for i in range(12):
            driver.set_pixel(i, 255, 0, 0)
        driver.show()
        power = LED(5)
        power.on()

        if text:
            print('Responding...')
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Answer as if you are J.A.R.V.I.S. from Iron Man. Address the user with Sir."},
                    {"role": "user", "content": text}])
            
            resp_str = response.choices[0].message.content
            
            print(resp_str)
            driver.clear_strip()
            return resp_str

        else:
            print('No text recognized')
            return None

    def play(self, response):
        
        driver = apa102.APA102(num_led=12)
        for i in range(12):
            driver.set_pixel(i, 0, 255, 0)
        driver.show()
        power = LED(5)
        power.on()
        
        print('Generating audio...')
        # George, Matthew. Joseph, Daniel
        audio = generate(
            text=response,
            voice="Matthew",
            model="eleven_monolingual_v1",
            stream=True
            )
        
        print('Playing audio...')
        stream(audio)

        driver.clear_strip()


    def run(self):

        text = self.listen()
        response = self.request(text)
        self.play(response)
    
  
if __name__ == '__main__':

    jv = Jarvis()
    jv.run()