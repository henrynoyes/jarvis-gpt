from submain import Jarvis, Shutdown
from pygame import mixer
from time import sleep

jv = Jarvis()

mixer.init()
mixer.music.load('./media/welcome_back.mp3')

try:
    mixer.music.play()
    
    jv.run()

except Shutdown:
    mixer.music.load('./media/shutting_down.mp3')
    mixer.music.play()
    sleep(2)