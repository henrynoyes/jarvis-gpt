import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import generate, stream
from elevenlabs.api import Voice
from gpiozero import LED
from apa102 import APA102
import sounddevice
from datetime import datetime
import json
from pyowm.owm import OWM

class Jarvis():

    def __init__(self):
        self.client = OpenAI()
        self.notes_path = './notes.json'
        self.driver = APA102(num_led=12)
        self.power = LED(5)
        self.func_dct = {
            'get_current_datetime': self.get_current_datetime,
            'get_current_weather': self.get_current_weather,
            'get_future_weather': self.get_future_weather,
            'record_note': self.record_note,
            'read_note': self.read_note,
            'remove_note': self.remove_note
        }
        self.gpt_funcs = [
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
                'name': 'record_note',
                'description': 'Record a note in the notes json file. Example: "Record a note that says {note}"',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'note': {
                            'type': 'string',
                            'description': 'The note to record in the json file',
                        }
                    },
                    'required': ['note'],
                },
            },
            {
                'name': 'read_note',
                'description': 'Read a note from the notes json file. Notes are organized by date and time. Example: "Read me my notes from {date}"',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'date': {
                            'type': 'string',
                            'description': f'The date label for the note. In the format "month-day-year". Today is {datetime.now().strftime("%m-%d-%Y")}',
                        }
                    },
                    'required': ['date'],
                },
            },
            {
                'name': 'remove_note',
                'description': 'Remove a note from the notes json file. Example: "Remove the first note from {date}"',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'date': {
                            'type': 'string',
                            'description': f'The date label for the note. In the format "month-day-year". Today is {datetime.now().strftime("%m-%d-%Y")}',
                        },
                        'index': {
                            'type': 'string',
                            'description': 'The index for the note to be removed. Convert the positional string to a number. Example: First = 0, Second = 1, Third = 2, and so on.'
                        }
                    },
                    'required': ['date', 'index'],
                },
            },
                ]
    
    def init_notes(self, notes_path):
        if not os.path.exists(notes_path):
            print('creating notes json')
            with open(notes_path, 'w') as f:
                json.dump(dict(), f)
        
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
    
    def record_note(self, note):
        now = datetime.now()
        date_str = now.strftime('%m-%d-%Y')
        time_str = now.strftime('%I:%M:%S %p')

        with open(self.notes_path, 'r') as f:
            notes_dct = json.load(f)

        if date_str in notes_dct:
            notes_dct[date_str][time_str] = note
        else:
            notes_dct[date_str] = {time_str: note}

        with open(self.notes_path, 'w') as f:
            json.dump(notes_dct, f)

        return {'status': 'complete', 'note': note}

    def read_note(self, date):
        print(date)

        with open(self.notes_path, 'r') as f:
            notes_dct = json.load(f)

        try:
            return_dct = notes_dct[date]
            status = 'complete'

        except:
            return_dct = notes_dct
            status = 'error'

        return {'status': status, 'notes': return_dct}

    def remove_note(self, date, index):
        print(date, index)

        with open(self.notes_path, 'r') as f:
            notes_dct = json.load(f)
        
        old_notes = notes_dct.copy()

        try:
            time = list(notes_dct[date])[int(index)]
            notes_dct[date].pop(time)
            status = 'complete'

            with open(self.notes_path, 'w') as f:
                json.dump(notes_dct, f)

        except:
            status = 'error: no note found'        

        return {'status': status, 'old notes': old_notes[date], 'updated notes': notes_dct[date]}

    def listen(self):

#         driver = apa102.APA102(num_led=12)
#         power = LED(5)
#         power.on()
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            # ambient adjustment causes longer delay
            r.adjust_for_ambient_noise(source)
            print("Listening...")
        
            self.power.on()
            for i in range(12):
                self.driver.set_pixel(i, 255, 100, 0)
            self.driver.show()
            
            audio = r.listen(source)
            self.driver.clear_strip()

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

            msgs = [{'role': 'system', 'content': 'You are a helpful assistant named Jarvis. Address the user with Sir. You can access the current date and time using get_current_datetime. \
                     You can access current weather information using get_current_weather. You can access weather forecasts up to 8 days in the future using get_future_weather. Do not ask the user for a location. \
                     Always report weather information in imperial units. You can read notes using read_note. You can record notes using record_note. You can remove notes using remove_note.'},
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
        
        for i in range(12):
            self.driver.set_pixel(i, 10, 100, 10)
        self.driver.show()
        
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

        self.driver.clear_strip()
        self.power.off()


    def run(self):

        self.init_notes(self.notes_path)
        text = self.listen()
        response = self.request(text)
        self.play(response)
    

if __name__ == '__main__':

    jv = Jarvis()
    jv.run()