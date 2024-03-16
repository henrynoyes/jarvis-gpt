import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from openai import OpenAI
from elevenlabs import generate, stream, Voice
from pyowm.owm import OWM
from datetime import datetime
import subprocess

class MorningJarvis():

    def __init__(self):
        self.client = OpenAI()
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

        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=msgs)
        
        resp_msg = response.choices[0].message
            
        print(resp_msg.content)
        return resp_msg.content
        
    def play(self, response):
        
        print('Generating audio...')

        jv_voice = Voice(voice_id=os.getenv('JARVIS_VOICEID'))

        audio = generate(
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