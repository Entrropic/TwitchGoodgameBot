from threading import Thread
import time
import YoutubeVideoTest
import GGBot
import TwitchBot

def invokeGG(music):
    GGBot.invoke(music)

def invokeTwitch(music):
    TwitchBot.invoke(music)

music = YoutubeVideoTest.MusicPlayer()
newone = Thread(target=invokeGG, args=(music,))
newtwo = Thread(target=invokeTwitch, args=(music,))

newone.start()
newtwo.start()

newone.join()
newtwo.join()

print("all threads finished.")






