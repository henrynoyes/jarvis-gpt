import speech_recognition as sr
from gpiozero import Button

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        print("Didn't get that. Try again")
        return ""
  
if __name__ == '__main__':

    button = Button(2)

    while True:
        if button.is_pressed:
            listen()
