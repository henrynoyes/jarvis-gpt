import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import generate, stream
from elevenlabs.api import Voice
from datetime import datetime
import sounddevice
import json
from pyowm.owm import OWM
from pygame import mixer
import time

class Jarvis():

    def __init__(self):
        self.client = OpenAI()
        # mixer.init()
        # mixer.music.load('./jarvis-startup.mp3')
        # mixer.music.set_volume(0.8)
        self.journal_path = './journal.json'
        self.gpt_funcs = [
            # {
            #     'name': 'get_current_datetime',
            #     'description': 'Get the current date and/or time',
            #     'parameters': {
            #         'type': 'object',
            #         'properties': {
            #             'mode': {
            #                 'type': 'string',
            #                 'enum': ['date', 'time', 'date & time'],
            #                 'description': 'Choose whether to get date, time, or both',
            #             }
            #         },
            #         'required': ['mode'],
            #     },
            # },
            {
                'name': 'get_current_datetime',
                'description': 'Get the current date and time',
            },
            {
                'name': 'get_current_weather',
                'description': 'Get the current weather for a given location',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'loc': {
                            'type': 'string',
                            'description': 'The city and country. For cities in the United States, it also includes the state. In the format "city,state,country"',
                        }
                    },
                    'required': [],
                },
            },
            {
                'name': 'get_future_weather',
                'description': 'Get the future weather forecast for a given location',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'days': {
                            'type': 'string',
                            'enum': [str(i) for i in range(1,9)],
                            'description': 'The number of days in the future for the weather forecast. Tomorrow is 1 day. A week from today is 7 days.'
                        },
                        'loc': {
                            'type': 'string',
                            'description': 'The city and country. For cities in the United States, it also includes the state. In the format "city,state,country"',
                        }
                    },
                    'required': ['days'],
                },
            },
            {
                'name': 'record_journal',
                'description': 'Record an entry in the journal json file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'entry': {
                            'type': 'string',
                            'description': 'The entry to record in the json file',
                        }
                    },
                    'required': ['entry'],
                },
            },
            {
                'name': 'read_journal',
                'description': 'Read an entry from the journal json file. Entries are organized by date and time.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'date': {
                            'type': 'string',
                            'description': f'The date label for the journal entry. In the format "month-day-year". Today is {datetime.now().strftime("%m-%d-%Y")}',
                        }
                    },
                    'required': ['date'],
                },
            },
            {
                'name': 'remove_journal',
                'description': 'Remove an entry from the journal json file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'date': {
                            'type': 'string',
                            'description': f'The date label for the journal entry. In the format "month-day-year". Today is {datetime.now().strftime("%m-%d-%Y")}',
                        },
                        'index': {
                            'type': 'string',
                            'description': 'The index for the journal entry to be removed. Convert the positional string to a number. Example: First = 0, Second = 1, Third = 2, and so on.'
                        }
                    },
                    'required': ['date', 'index'],
                },
            },
                ]
        
    def init_journal(self, journal_path):
        if not os.path.exists(journal_path):
            print('creating journal json')
            with open(journal_path, 'w') as f:
                json.dump(dict(), f)

    # def get_current_datetime(self, mode='date & time'):
    #     now = datetime.now()
    #     date_str = now.strftime('%m-%d-%Y')
    #     time_str = now.strftime('%I:%M:%S %p')  
        
    #     if mode == 'date':
    #         return {'datetime': date_str}
    #     elif mode == 'time':
    #         return {'datetime': time_str}
    #     else:
    #         return {'datetime': f'{date_str} {time_str}'}
        
    def get_current_datetime(self):
        now = datetime.now()
        date_str = now.strftime('%m-%d-%Y')
        time_str = now.strftime('%I:%M:%S %p')
        
        return {'date': date_str, 'time': time_str}
    
    def get_current_weather(self, loc=os.getenv('JARVIS_LOCATION')):

        print(loc)

        owm = OWM(os.getenv('OWM_API_KEY'))

        coder = owm.geocoding_manager()
        loc_info = coder.geocode(loc)[0]

        mgr = owm.weather_manager()
        info = mgr.one_call(lon=loc_info.lon, lat=loc_info.lat, units='imperial', exclude=['minutely', 'hourly', 'daily', 'alerts'])

        forecast = info.current

        return forecast.to_dict()
    
    def get_future_weather(self, days, loc=os.getenv('JARVIS_LOCATION')):

        print(days, loc)

        owm = OWM(os.getenv('OWM_API_KEY'))

        coder = owm.geocoding_manager()
        loc_info = coder.geocode(loc)[0]

        mgr = owm.weather_manager()
        info = mgr.one_call(lon=loc_info.lon, lat=loc_info.lat, units='imperial', exclude=['minutely', 'hourly', 'alerts'])

        forecast = info.forecast_daily[int(days)]

        return forecast.to_dict()
    
    def record_journal(self, entry):
        now = datetime.now()
        date_str = now.strftime('%m-%d-%Y')
        time_str = now.strftime('%I:%M:%S %p')

        with open(self.journal_path, 'r') as f:
            journal_dct = json.load(f)

        if date_str in journal_dct:
            journal_dct[date_str][time_str] = entry
        else:
            journal_dct[date_str] = {time_str: entry}

        with open(self.journal_path, 'w') as f:
            json.dump(journal_dct, f)

        return {'status': 'complete', 'entry': entry}

    def read_journal(self, date):
        print(date)

        with open(self.journal_path, 'r') as f:
            journal_dct = json.load(f)

        try:
            return_dct = journal_dct[date]
            status = 'complete'

        except:
            return_dct = journal_dct
            status = 'error: no journal entry found'

        return {'status': status, 'journal': return_dct}

    def remove_journal(self, date, index):
        print(date, index)

        with open(self.journal_path, 'r') as f:
            journal_dct = json.load(f)
        
        old_journal = journal_dct.copy()

        try:
            time = list(journal_dct[date])[int(index)]
            journal_dct[date].pop(time)
            status = 'complete'

            with open(self.journal_path, 'w') as f:
                json.dump(journal_dct, f)

        except:
            status = 'error: no journal entry found'        

        return {'status': status, 'old journal': old_journal[date], 'updated journal': journal_dct[date]}

    def listen(self):
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            # ambient adjustment causes longer delay
            r.adjust_for_ambient_noise(source)
            print('Listening...')
            
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

        func_dct = {
            'get_current_datetime': self.get_current_datetime,
            'get_current_weather': self.get_current_weather,
            'get_future_weather': self.get_future_weather,
            'record_journal': self.record_journal,
            'read_journal': self.read_journal,
            'remove_journal': self.remove_journal
        }

        if text:
            print('Responding...')

            msgs = [{'role': 'system', 'content': 'You are a helpful assistant named Jarvis. Address the user with Sir. You can access the current date and time using get_current_datetime. \
                     You can access current weather information using get_current_weather. You can access weather forecasts up to 8 days in the future using get_future_weather. Do not ask the user for a location. \
                     Always report weather information in imperial units. You can read journal entries using read_journal. You can record journal entries using record_journal. You can remove journal entries using remove_journal.'},
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
                func_to_call = func_dct[func_name]
                func_response = func_to_call(**func_args)
                print(f'Calling {func_name}...')

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

        else:
            print('No text recognized')
            return None

    def play(self, response):
        
        print('Generating audio...')

        # jv_voice = Voice.from_id(os.getenv('JARVIS_VOICEID'))

        # audio = generate(
        #     text=response,
        #     voice=jv_voice,
        #     model='eleven_multilingual_v2',
        #     stream=True
        #     )
        
        # print('Playing audio...')
        # stream(audio)

    def run(self):

        # mixer.music.play()
        # time.sleep(15)
        self.init_journal(self.journal_path)
        text = self.listen()
        response = self.request(text)
        self.play(response)
    
  
if __name__ == '__main__':

    jv = Jarvis()
    jv.run()