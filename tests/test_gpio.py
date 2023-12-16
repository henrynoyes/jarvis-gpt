from gpiozero import Button

button = Button(pin=12)

while True:
    if button.is_pressed:
        print('pressed')