import speech_recognition as sr
from openai import OpenAI
from elevenlabs import generate, stream

class Jarvis():

    def __init__(self):
        self.client = OpenAI()

    def listen(self):
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            # ambient adjustment causes longer delay
            r.adjust_for_ambient_noise(source)
            print("Listening...")
            
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
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Answer as if you are J.A.R.V.I.S. from Iron Man. Address the user with Sir."},
                    {"role": "user", "content": text}])
            
            resp_str = response.choices[0].message.content
            
            print(resp_str)
            return resp_str

        else:
            print('No text recognized')
            return None

    def play(self, response):
        
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

    def run(self):

        text = self.listen()
        response = self.request(text)
        self.play(response)
    
  
if __name__ == '__main__':

    jv = Jarvis()
    jv.run()