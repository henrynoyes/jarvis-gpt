from phue import Bridge
import os

ip = os.getenv('PHUE_IP')
b = Bridge(ip)

current_state = b.get_light('pixar', 'on')
print(type(current_state), current_state)

current_bri = b.get_light('pixar', 'bri')
print(type(current_bri), current_bri)
