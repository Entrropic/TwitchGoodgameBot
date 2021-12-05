import os
import json
import sys
import time
import requests
import YoutubeVideoTest
import asyncio
from twitchio.ext import commands



datapath = os.path.dirname(os.path.realpath(__file__))+'\\twitchbotdata.txt'
data = json.loads(open(datapath, 'r').read())

BOT_USERNAME = data["login"]
CHANNEL_NAME = data["ch_name"]
OAUTH = data["oauth"]

print(data) #debug

#bot = Bott(OAUTH, CHANNEL_NAME)
#bot.run()
messagebucket = str()
def invoke(music):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = commands.Bot(token=OAUTH, prefix='!', initial_channels=[CHANNEL_NAME])

    if music == None:
        music = YoutubeVideoTest.MusicPlayer()

    @bot.event()
    async def event_ready():
       print('Logged in as ' + BOT_USERNAME)

    @bot.event()
    async def event_message(msg):
        if msg.author is not None:
           if msg.author.name == BOT_USERNAME:
               return

           if BOT_USERNAME.lower() in msg.content.lower():
               print("detect something addressed at me")
               await msg.channel.send('@' + msg.author.name + ', Вы обращаетесь ко мне, но делаете это без уважения.')

           global messagebucket #an ugly way to get message in !play command
           messagebucket = msg.content
           if messagebucket == msg.content:
               await bot.handle_commands(msg)

    #@bot.command(name='test')
    #async def test(ctx):
     #  await ctx.send("test test test")

    @bot.command(name='AOE4rank', aliases=['aoe4rank'])
    async def AOE4rank(ctx):
        rank_r = requests.post("https://api.ageofempires.com/api/ageiv/Leaderboard",
                               json={"region": "7", "versus": "players", "matchType": "unranked", "teamSize": "1v1",
                                     "searchPlayer": "entrropical", "page": 1, "count": 100},
                               headers={'Content-Type': 'application/json'})

        if rank_r.status_code == 200:
            parsed = json.loads(rank_r.content)['items'][0]
            await ctx.send("Игрок " + parsed["userName"] +
                                " находится на позиции " + str(parsed["rank"]) +
                                " среди всех игроков Age of Empires 4, сыгравших 10 и более матчей. "
                                "ЭЛО: " + str(parsed["elo"]) +
                                ", побед: " + str(parsed["wins"]) +
                                ", поражений: " + str(parsed["losses"]) +
                                ", винрейт: " + str(parsed["winPercent"]) + "%.")
        else:
            await ctx.send("Не смог запросить результаты из таблицы рекордов age of empires 4, код ошибки на запрос: "
                     + str(rank_r.status_code))

    @bot.command(name='play')
    async def addmusictoqueue(ctx):
        temp = messagebucket
        if len(temp) > 0:
            print(temp)
            p = 0
            while p < len(temp) and temp[p:p + len("https://")] != "https://" and temp[p:p + len("http://")] != "http://" and temp[p:p + len("www.")] != "www.":
                p += 1
            if p < len(temp):
                s = temp[p:len(temp)]
                check = music.Add(s)
                if check == 0:
                    await ctx.send("Добавил ссылку в очередь.")
                elif check == -1:
                    await ctx.send("Непохоже на ссылку с youtube. DansGame ")
                elif check == -2:
                    await ctx.send("Видео больше 15 минут не принимаю. BabyRage ")
                elif check == -3:
                    await ctx.send("Эту ссылку уже ранее добавляли.")
            else:
                await ctx.send(ctx.author.name + ", есть ссылка? А если найду? DansGame ")

    @bot.command(name='queue')
    async def musicqueue(ctx):
        await ctx.send(music.ShowQueue())

    @bot.command(name='exit')
    async def quitnow(ctx):
        await bot.close()
    bot.run()

if __name__ == "__main__":
    invoke(None)

print("quitting")