import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import generate, stream
from elevenlabs.api import Voice
import sounddevice
from datetime import datetime
import json

class Shutdown(Exception):
    pass

class Jarvis():

    def __init__(self):
        self.client = OpenAI()
        self.func_dct = {
            'shutdown': self.shutdown,
            'get_current_datetime': self.get_current_datetime,
        }
        self.gpt_funcs = [
            {
                'name': 'shutdown',
                'description': 'Begin shutdown sequence',
            },
            {
                'name': 'get_current_datetime',
                'description': 'Get the current date and time',
            },
                ]

    def shutdown(self):

        print('raising exception')
        raise Shutdown
        
    def get_current_datetime(self):
        now = datetime.now()
        date_str = now.strftime('%m-%d-%Y')
        time_str = now.strftime('%I:%M:%S %p')
        
        return {'date': date_str, 'time': time_str}
    
    def listen(self):
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                # ambient adjustment causes longer delay
                r.adjust_for_ambient_noise(source)
                print("Listening...")
            
                audio = r.listen(source, timeout=6)

                print('Recognizing...')
                text = r.recognize_google(audio)
                print(text)
                return text

            except sr.WaitTimeoutError:
                print('timed out')
                return None

            except:
                print(f'no text recognized')
                return None
        
    def request(self, text):

        print('Responding...')

        msgs = [{'role': 'system', 'content': 'You are a helpful assistant named Jarvis. Address the user with Sir. \
                 You can access the current date and time using get_current_datetime. ALWAYS BE CONCISE.'},
                    {'role': 'user', 'content': text}]

        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=msgs,
            functions=self.gpt_funcs,
            function_call='auto')
        
        resp_msg = response.choices[0].message

        if resp_msg.function_call:
            func_name = resp_msg.function_call.name
            func_args = json.loads(resp_msg.function_call.arguments)
            func_to_call = self.func_dct[func_name]

            print(f'Calling {func_name}...')
            func_response = func_to_call(**func_args)
            if func_response:
                msgs.append(
                    {
                        "role": "function",
                        "name": func_name,
                        "content": json.dumps(func_response),
                    }
                )

                print('Function Responding...')
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=msgs,)
                
                resp_msg = response.choices[0].message
            
        print(resp_msg.content)
        return resp_msg.content
        
    def play(self, response):
        
        print('Generating audio...')

        jv_voice = Voice.from_id(os.getenv('JARVIS_VOICEID'))

        audio = generate(
            text=response,
            voice=jv_voice,
            model='eleven_multilingual_v2',
            stream=True
            )
        
        print('Playing audio...')
        stream(audio)

    def run(self):

        text = self.listen()
        if text:
            response = self.request(text)
            if response:
                self.play(response)