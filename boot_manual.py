from main import Jarvis, Shutdown
from pygame import mixer
from time import sleep
from pynput import keyboard

jv = Jarvis()
mixer.init()
mixer.music.load('./media/welcome_back.mp3')

def on_press(key):
    global jv
    try:
        if key.char == 'j':
            sleep(0.2)
            print('\nJARVIS activated')
            mixer.music.play()
            sleep(8)
            jv.run()

    except Shutdown:
        mixer.music.load('./media/shutting_down.mp3')
        mixer.music.play()
        sleep(2)

    except AttributeError:
        pass

print('JARVIS interface activated | Press j to begin listening')
listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()