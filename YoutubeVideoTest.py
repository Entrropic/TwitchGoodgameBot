import pafy
import os
os.add_dll_directory(r'C:\Program Files\VLC')
import vlc
#redesign it so length and validity checks occur when it adds videos to queue.
# Also store video names separately so they can be called by separate command

"""
functionality:
1. plays music videos from youtube
2. checks input of !play command for validity
"""

class MusicPlayer():
    queue = list()
    check = set()
    media = vlc.MediaPlayer()
    def Play(self):
        if not self.media.is_playing() and len(self.queue)>0:
            """ started = False
            while not started:
               try:
                   n = pafy.new(self.queue[0])
               except ValueError:
                   self.check.discard(self.queue[0])
                   del self.queue[0]
                   output = "Непохоже на ссылку с youtube. :fuckoff: "
                   return output
               except:
                  print("trying again")
               else:
                  started = True"""
            n = self.queue[0][0]
            output = "Начинаю воспроизведение: "+n.title
            best = n.getbestaudio()
            self.media = vlc.MediaPlayer(best.url)
            self.media.audio_set_volume(30)
            self.media.play()

            self.check.discard(self.queue[0][1])
            del self.queue[0]
            return output
        else:
            return None

    def Add(self, url: str) -> int: #needs to return 0 if success, -1 if fail, -2 if too long video, -3 if URL already was added before. Adds pafy.new object
        if url not in self.check:
          while True:
            try:
                n = pafy.new(url)
            except ValueError:
                #output = "Непохоже на ссылку с youtube. :fuckoff: "
                return -1
            except:
                print("trying again")
            else:
                if n.length > 15 * 60:
                    return -2
                else:
                    self.queue.append([n, url])
                    self.check.add(url)
                    return 0
        else:
          return -3

    def ShowQueue(self) -> str:
        if len(self.queue) == 0:
            return "Кажется, в очереди ничего нет. :pepehands: "
        else:
            return "Очередь на текущий момент: "+", ".join([str(i+1)+". "+self.queue[i][0].title for i in range(len(self.queue))])

    def Remove(self, i: int):
        if i<=len(queue) and i>0:
            self.check.discard(self.queue[i-1][1])
            del self.queue[i-1]
        return

