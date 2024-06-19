import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import Voice, stream
from elevenlabs.client import ElevenLabs
from time import sleep
from gpiozero import LED
from apa102 import APA102
import sounddevice
from datetime import datetime
import json
import yaml
from pyowm.owm import OWM
from phue import Bridge
from ws import WSClient
import pyautogui as pyg

class Shutdown(Exception):
    pass

class Jarvis:

    def __init__(self):
        self.oai_client = OpenAI()
        self.elev_client = ElevenLabs()
        self.ws_client = WSClient()
        self.notes_path = '/home/jarvis/jarvis-gpt/notes.json'
        self.led_driver = APA102(num_led=12)
        self.led_power = LED(5)
        self.bridge = Bridge(os.getenv('PHUE_IP'))
        self.owm = OWM(os.getenv('OWM_API_KEY'))
        self.logo_dct = {'home': (1100, 76),
                         'timer': (337, 50)}
        self.func_dct = {
            'shutdown': self.shutdown,
            'get_current_datetime': self.get_current_datetime,
            'get_current_weather': self.get_current_weather,
            'get_future_weather': self.get_future_weather,
            'record_note': self.record_note,
            'read_note': self.read_note,
            'remove_note': self.remove_note,
            'power_lights': self.power_lights,
            'change_brightness': self.change_brightness,
            'recolor_model': self.recolor_model,
            'start_timer': self.start_timer,
            'switch_dashboard': self.switch_dashboard
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
            {
                'name': 'power_lights',
                'description': 'Turn the desired lights on or off',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'desired_light': {
                            'type': 'string',
                            'enum': ['pixar', 'green', 'all'],
                            'description': 'The desired lights to turn on/off. Choose "all" if no light name is specified.',
                        },
                        'desired_state': {
                            'type': 'string',
                            'enum': ['on', 'off'],
                            'description': 'The desired state of the lights',
                        }
                    },
                    'required': ['desired_light', 'desired_state'],
                },
            },
            {
                'name': 'change_brightness',
                'description': 'Change the brightness of the lights',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'desired_light': {
                            'type': 'string',
                            'enum': ['pixar', 'green', 'all'],
                            'description': 'The desired lights to change. Choose "all" if no light name is specified.',
                        },
                        'desired_percent': {
                            'type': 'string',
                            'description': 'The desired brightness percentage number as an integer',
                        }
                    },
                    'required': ['desired_light', 'desired_percent'],
                },
            },
            {
                'name': 'recolor_model',
                'description': 'Recolor a 3D model',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'current_color': {
                            'type': 'string',
                            'description': 'The current color to modify on the 3D model',
                        },
                        'new_color': {
                            'type': 'string',
                            'description': 'The new color to use on the 3D model',
                        }
                    },
                    'required': ['current_color', 'new_color'],
                },
            },
            {
                'name': 'start_timer',
                'description': 'Start a timer',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'desired_length': {
                            'type': 'string',
                            'description': 'The desired length of the timer in integer minutes',
                        }
                    },
                    'required': ['desired_length'],
                },
            },
            {
                'name': 'switch_dashboard',
                'description': 'Switch to a specified dashboard',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'desired_dashboard': {
                            'type': 'string',
                            'enum': ['home', 'timer'],
                            'description': 'The desired dashboard to switch to. Choose "home" if no dashboard name is specified.',
                        }
                    },
                    'required': ['desired_dashboard'],
                },
            },
                ]
    
    def startup(self):

        with open('/home/jarvis/jarvis-gpt/config.yaml', 'r') as f:
            cfg_dct = yaml.safe_load(f)

            if cfg_dct['startup_lights']:
                self.power_lights(cfg_dct['startup_lights'], 'on')
                self.change_brightness(cfg_dct['startup_lights'], cfg_dct['startup_brightness'])

        self.led_power.on()
        for i in range(12):
            self.led_driver.set_pixel(i, 0, 255, 255)
            self.led_driver.show()
            sleep(0.66)
        self.led_driver.clear_strip()

    def shutdown(self):
        
        with open('/home/jarvis/jarvis-gpt/config.yaml', 'r') as f:
            cfg_dct = yaml.safe_load(f)

            if cfg_dct['shutdown_lights']:
                self.power_lights(cfg_dct['shutdown_lights'], 'off')

        print('raising exception')
        raise Shutdown
        
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
    
    def power_lights(self, desired_light, desired_state):
        print(desired_light, desired_state)

        bool_dct = {'on': True, 'off': False}
        bool_state = bool_dct[desired_state]

        light_dct = self.bridge.get_light_objects('name')

        name_lst = [desired_light]
        if desired_light =='all':
            name_lst = list(light_dct.keys())
            name_lst.remove('JARVIS Plug')

        for name in name_lst:
            current_state = light_dct[name].on
            if bool_state == current_state:
                return {'status': f'The {name} light is already {desired_state}', 'state': desired_state}
            light_dct[name].on = bool_state

        return None
    
    def change_brightness(self, desired_light, desired_percent):
        print(desired_light, desired_percent)

        desired_bri = int(int(desired_percent) * 2.54)

        print(desired_bri)

        if desired_bri < 0 or desired_bri > 254:
            return {'status': 'Error: The requested brightness is not valid', 'brightness': desired_percent}
        
        light_dct = self.bridge.get_light_objects('name')

        name_lst = [desired_light]
        if desired_light =='all':
            name_lst = list(light_dct.keys())
            name_lst.remove('JARVIS Plug')

        for name in name_lst:
            power_status = light_dct[name].on
            if not power_status:
                return {'status': f'Error: The {name} light is not on'}

            current_bri = light_dct[name].brightness
            if desired_bri == current_bri:
                return {'status': f'The {name} light is already at {desired_percent} percent brightness', 'brightness': desired_percent}

            light_dct[name].brightness = desired_bri

        return None

    def recolor_model(self, current_color, new_color):
        args = {'current_color': current_color,
                'new_color': new_color}
        msg = {'name': 'recolor_model',
               'arguments': args}
        self.ws_client.run(json.dumps(msg))
        return self.ws_client.resp_dct
    
    def dash(self, x, y):
        pyg.moveTo(x, y)
        pyg.click()
        sleep(1)

    def switch_dashboard(self, desired_dashboard):

        x, y = self.logo_dct[desired_dashboard]
        self.dash(x, y)
        return None
    
    def start_timer(self, desired_length):
        
        tx, ty = self.logo_dct['timer']
        self.dash(tx, ty)
        self.dash(560, 209)

        pyg.press('backspace')
        sleep(1)
        pyg.write(desired_length)
        sleep(1)

        self.dash(800, 500)
        
        return {'status': 'timer started', 'length': desired_length}
    
    def listen(self):
        
        self.led_power.on()
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                # ambient adjustment causes longer delay
                r.adjust_for_ambient_noise(source)
                print("Listening...")
            
                for i in range(12):
                    self.led_driver.set_pixel(i, 255, 100, 0)
                self.led_driver.show()
                
                audio = r.listen(source, timeout=6)
                self.led_driver.clear_strip()

                print('Recognizing...')
                text = r.recognize_google(audio)
                print(text)
                return text

            except sr.WaitTimeoutError:
                self.led_driver.clear_strip()
                print('timed out')
                return None

            except:
                print(f'no text recognized')
                return None
        
    def request(self, text):

        print('Responding...')

        msgs = [{'role': 'system', 'content': 'You are a helpful assistant named Jarvis. Address the user with Sir. You can access the current date and time using get_current_datetime. \
                    You can access current weather information using get_current_weather. You can access weather forecasts up to 8 days in the future using get_future_weather. Do not ask the user for a location. \
                    Always report weather information in imperial units. You can read notes using read_note. You can record notes using record_note. You can remove notes using remove_note. \
                    You can turn the lights on/off using power_lights. You can change the light brightness using change_brightness. You can color 3D models using recolor_model. \
                    You can switch dashboards using switch_dashboard. You can start a timer using start_timer. ALWAYS BE CONCISE.'},
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
        
        for i in range(12):
            self.led_driver.set_pixel(i, 10, 100, 10)
        self.led_driver.show()
        
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

        self.led_driver.clear_strip()
        self.led_power.off()

    def run(self):

        self.init_notes(self.notes_path)
        text = self.listen()
        if text:
            response = self.request(text)
            if response:
                self.play(response)
