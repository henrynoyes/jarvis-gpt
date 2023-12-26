import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import mixer
from time import sleep

mixer.init()
mixer.music.load('../media/welcome_back.mp3')
#mixer.music.set_volume(1)
mixer.music.play()
sleep(10)
