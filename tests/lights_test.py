from phue import Bridge
import os

ip = os.getenv('PHUE_IP')
b = Bridge(ip)

print(b.get_api())
