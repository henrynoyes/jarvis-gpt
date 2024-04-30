import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import stream, Voice
from elevenlabs.client import ElevenLabs
from pyowm.owm import OWM
from datetime import datetime
import subprocess
import json

class MorningJarvis():

    def __init__(self):
        self.oai_client = OpenAI()
        self.elev_client = ElevenLabs()
        self.owm = OWM(os.getenv('OWM_API_KEY'))
        
    def get_current_datetime(self):
        now = datetime.now()
        date_str = now.strftime('%A %B %d')
        time_str = now.strftime('%I:%M %p')
        
        return {'date': date_str, 'time': time_str}
    
    def get_current_weather(self, loc=os.getenv('JARVIS_LOCATION')):

        print(loc)

        coder = self.owm.geocoding_manager()
        loc_info = coder.geocode(loc)[0]

        mgr = self.owm.weather_manager()
        info = mgr.one_call(lon=loc_info.lon, lat=loc_info.lat, units='imperial', exclude=['minutely', 'hourly', 'daily', 'alerts'])

        forecast = info.current

        return forecast.to_dict()
    
    def get_future_weather(self, days, loc=os.getenv('JARVIS_LOCATION')):

        print(days, loc)

        coder = self.owm.geocoding_manager()
        loc_info = coder.geocode(loc)[0]

        mgr = self.owm.weather_manager()
        info = mgr.one_call(lon=loc_info.lon, lat=loc_info.lat, units='imperial', exclude=['minutely', 'hourly', 'alerts'])

        forecast = info.forecast_daily[int(days)]

        return forecast.to_dict()
        
    def request(self, text):

        print('Responding...')

        msgs = [{'role': 'system', 'content': 'You are a helpful assistant named Jarvis. Address the user with Sir. ALWAYS BE CONCISE.'},
                    {'role': 'user', 'content': text}]

        response = self.oai_client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=msgs)
        
        resp_msg = response.choices[0].message
            
        print(resp_msg.content)
        return resp_msg.content
        
    def play(self, response):
        
        print('Generating audio...')

        jv_voice = Voice(voice_id=os.getenv('JARVIS_VOICEID'))

        audio = self.elev_client.generate(
            text=response,
            voice=jv_voice,
            model='eleven_multilingual_v2',
            stream=True
            )
        
        print('Playing audio...')
        stream(audio)

    def run(self, text):

        response = self.request(text)
        self.play(response)

class Notifetcher():

    def fetch(self):

        out_str = subprocess.run(['osascript', '/Users/henry/jarvis-gpt/notif.scpt'], capture_output=True, text=True, check=True)
        out_lst = out_str.stdout.replace('\n', '').split(', ')
        
        notif_lst = [{'Total Notifications': len(out_lst)}]

        for notif_str in out_lst:
            data = notif_str.split('||')

            dct = {
                'Time': data[0],
                'Title': data[1],
                'Description': data[2]
            }

            notif_lst.append(dct)

        return notif_lst

class Shutdown(Exception):
    pass

class Jarvis():

    def __init__(self):
        self.oai_client = OpenAI()
        self.elev_client = ElevenLabs()
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

        response = self.oai_client.chat.completions.create(
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
                response = self.oai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=msgs,)
                
                resp_msg = response.choices[0].message
            
        print(resp_msg.content)
        return resp_msg.content
        
    def play(self, response):
        
        print('Generating audio...')

        jv_voice = Voice.from_id(os.getenv('JARVIS_VOICEID'))

        audio = self.elev_client.generate(
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