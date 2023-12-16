from gpiozero import Button
from main import Jarvis

button = Button(pin=12)
jv = Jarvis()

while True:
    if button.is_pressed:
        jv.run()