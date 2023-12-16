from grove.gpio import GPIO

button = GPIO(12, GPIO.IN)

while True:
    if button.read():
        print('pressed')