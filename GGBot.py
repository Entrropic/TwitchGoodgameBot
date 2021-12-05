# -*- coding: utf8 -*-

#todo: regulate the amount of stream currency granted. should be 1 per minute, not 1 per 0.5 seconds or whatever.
#regedign !nuke so it targets a specific user.
#also possibly work on creating GUI and more customization during runtime

import time
import websocket
import json
import requests
import random
import os
import asyncio
import YoutubeVideoTest
import StreamCurrencyManager

"""
functionality:
1. primary file of chatbot, manages tasks and interacts with chat. Launch bot from this file
2. loads other modules.
"""

class TaskSchedule():
    tasks = list()
    nextmsgtime = int
    currencyworks = set()
    streamcurrency = None
    laststuff = None
    g_socket = None
    idchannel = str()
    occasionalphrases = list()
    #task unit - dictionary.
    #{"type": one of: "greeting", "hatemsg" (possibly add more later),
    #"content": content of message probably (depending on event may be smth else)
    #for some tasks I also transfer "id" for now. In reality depending on type tasks should have different stuff in them
    #"time": time when even should be executed. To compare with time.time() function. If its bigger or equal, execute event}

    def __init__(self, streamcurrency, laststuff, g_socket, idchannel):
        self.nextmsgtime = time.time()+ 60*60
        self.streamcurrency = streamcurrency
        self.laststuff = laststuff
        self.g_socket = g_socket
        self.idchannel = idchannel
        self.occasionalphrases = ["Ну че, кожаные мешки, как дела?",
                             "Чет скучно стало",
                             ":doggie:"]

    def lookup(self):#should look up through tasks. If any are up for execution - run their procedures.
        i = 0
        while i<len(self.tasks):
            if self.tasks[i]["time"]<=time.time():
                if self.tasks[i]["type"]=="greeting":
                    self.greet(self.tasks[i]["content"])
                elif self.tasks[i]["type"]=="hatemsg":
                    self.hate(self.tasks[i]["content"], self.tasks[i]["id"])
                elif self.tasks[i]["type"]=="savedata":
                    self.savedat()
                elif self.tasks[i]["type"]=="grantcurr":
                    self.grantcur(self.tasks[i]["content"])
                del self.tasks[i]
            else:
                i+=1
        if self.nextmsgtime<=time.time():
            self.occasionalmsg()

    def occasionalmsg(self):
        self.g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': self.idchannel,
                                                                   'text': self.occasionalphrases[random.randrange(len(self.occasionalphrases))],
                                                                   'hideIcon': False, 'mobile': False}}))
        self.nextmsgtime = time.time()+ 60*60

    def greet(self, msg: str):
        self.g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': self.idchannel,
                                                                   'text': msg,
                                                                   'hideIcon': False, 'mobile': False}}))
        self.addtime(30)
        time.sleep(0.5)

    def hate(self, msg: str, id: int):
        if boolhatred:
            self.g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': self.idchannel,
                                                                       'text': msg,
                                                                       'hideIcon': False, 'mobile': False}}))
            self.g_socket.send(json.dumps({'type': "warn",
                                      'data': {'channel_id': self.idchannel, 'user_id': id,
                                               'reason': ":fuckoff:"}}))
            self.addtime(30)

            time.sleep(0.5)
            self.addtask({"type": "hatemsg",
                          "content": hated+", :fuckoff:",
                          "id" : id,
                          "time": time.time()+10})

    def savedat(self):
        writestuff = open(os.path.dirname(os.path.realpath(__file__))+'\\botdata.txt', 'w')
        writestuff.write(json.dumps(self.laststuff))
        writestuff.close()
        self.streamcurrency.SaveIntoFile()
        self.addtask({"type": "savedata",
                       "time": time.time() + 60})

    def grantcur(self, content):
        self.streamcurrency.GrantCurrency(content["user"], content["amount"])
        try:
            self.currencyworks.remove(content["user"]["name"])
        except KeyError:
            print("something wrong, tried to remove user not present in tasks set. Look at this later")
        return

    def addtask(self, task: dict):
        if task["type"] == "grantcurr":
            if task["content"]["user"]["name"] in self.currencyworks: return
            else: self.currencyworks.add(task["content"]["user"]["name"])
        self.tasks.append(task)

    def addtime(self, addition):
        self.nextmsgtime+=addition


#get token for auth
def login(login, pw) -> list:
    gettoken = requests.post(url="https://goodgame.ru/ajax/chatlogin", data={'login': login, 'password': pw})  # headers={'content-type': 'x-www-form-urlencoded'})

    return[json.loads(gettoken.text)["user_id"], json.loads(gettoken.text)["token"]]

def invoke(music):
    #wss://chat.goodgame.ru/chat/websocket
    #wss://chat-1.goodgame.ru/chat2/websocket/ # protocol2. Also works.
    #websocket.enableTrace(True)
    g_socket = websocket.WebSocket()

    g_socket.connect("wss://chat-1.goodgame.ru/chat2/websocket/") #IMPORTANT - "chat" after wss changed to "chat-1", "chat" after goodgame.ru changed to chat2

    getstuff = open(os.path.dirname(os.path.realpath(__file__))+'\\botdata.txt', 'r')#used to be 'D:\\botdata.txt'

    laststuff = json.loads(getstuff.read())
    getstuff.close()
    #prototype for data stored in botdata:
    #{"login" : "login", "password" : "password", "ch_id" : "channel id", "timestamp": int(timestamp of last msg), "feedtime": int(time the !feed command is used)}

    #g_socket.send(json.dumps({'type': "auth", 'data': {'user_id': 'trash', 'token': 'no'}}))
    botlogin = laststuff["login"]
    botpass = laststuff["password"]
    idchannel = laststuff["ch_id"]

    userdata = login(botlogin, botpass)
    print(userdata)

    #(userdata[0] is id, userdata[1] is token)
    g_socket.send(json.dumps({'type': "auth", 'data': {'user_id': userdata[0], 'token': userdata[1]}}))
    time.sleep(1)
    print(g_socket.recv())
    g_socket.send(json.dumps({'type': "join", 'data': {'channel_id': idchannel, 'hidden': False}}))
    time.sleep(1)
    print(g_socket.recv())
    time.sleep(1)
    print(g_socket.recv())
    time.sleep(1)
    print(g_socket.recv())

    stay_online = True

    #feedcounter = laststuff["feedtime"] For now adding for clarity
    #timestampofmsg = laststuff["timestamp"]

    hated = 'badWiedzmin'
    boolhatred = False
    hatedDetected = False
    hatedelay = 0
    emptystr = ""

    greeted = set()

    if music == None: #for solo calling
        music = YoutubeVideoTest.MusicPlayer()
    streamcurrency = StreamCurrencyManager.CurrencyManager(os.path.dirname(os.path.realpath(__file__)))

    tasks = TaskSchedule(streamcurrency, laststuff, g_socket, idchannel)
    tasks.addtask({"type": "savedata",
                   "time": time.time() + 10 * 60})

    botphrases=[
    "ты что от бота хочешь?",
    "специально для тебя тотем подготовил, присаживайся.",
    "reported за токсичность, надеюсь, тебя забанят!",
    "ПвП или зассал?",
    "я твой отец.",
    "ты чего такой серьёзный?",
    "ты обращаешься ко мне, но делаешь это без уважения.",
    "с чизерками не разговариваю.",
    "я твой чат сообщения шатал.",
    "кожаный мешок, что ты о себе возомнил?",
    "поцелуй мой сияющий металлический зад!",
    "не читал, но осуждаю.",
    "буду краток. :fuckoff:"]

    botwelcome=[
    "добро пожаловать! :cat:",
    "я тебя вижу, выходи. :pled:",
    "проходи, гостем будешь. :fibod:",
    "эн таро Тассадар, путник. :toss:",
    "да прибудет с тобой сила. :buff:",
    ":vjuh: вжух и +1 зритель.",
    "а не тимо-мейнер ли ты случаем? :sosp:"
    ]

    modsids = {181773, 486867}

    random.seed()

    try:
     while stay_online:
        #g_socket.send(json.dumps({'type': "send_message",
        #                          'data': {'channel_id': "166776", 'text': "тестовое сообщение "+str(i+1), 'hideIcon': False,
        #                                   'mobile': False}}))
        try:
         tasks.lookup()
        except Exception as e:
            log = open(os.path.dirname(os.path.realpath(__file__)) + '\\errorlog.txt', 'a')
            log.write("[" + time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(time.time())) + "] error during task lookup: " + str(e) + '\n')
            log.close()
        songname = music.Play()
        if songname != None:
            g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': songname, 'hideIcon': False, 'mobile': False}}))
            time.sleep(0.2)

        g_socket.send(json.dumps({'type': "get_users_list2", 'data': {'channel_id': idchannel}}))

        userlist = json.loads(g_socket.recv())
        while (userlist["type"]) != "users_list":
            userlist = json.loads(g_socket.recv())

        g_socket.send(json.dumps({'type': "get_channel_history", 'data': {'channel_id': idchannel, 'hidden': True}}))
        messagelist = json.loads(g_socket.recv())
        while (messagelist["type"]) != "channel_history":
            messagelist = json.loads(g_socket.recv())

        #print(messagelist["data"]["messages"])
        try:
         for i in range(len(messagelist["data"]["messages"])):
          if laststuff["timestamp"]<messagelist["data"]["messages"][i]["timestamp"]:
            if messagelist["data"]["messages"][i]["text"][0]=="!":
                if messagelist["data"]["messages"][i]["text"][:len("!help ")].strip() == "!help":
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                               'text': "Список команд: "
                                                                                       "!help - вызвать эту справку, "
                                                                                       "!toxic - включение хейта бэда (только для модераторов), "
                                                                                       "!stop - отключение хейта бэда (только для модераторов), "
                                                                                       "!feed - счётчик фидов, !trash - удаление сообщений бэда, "
                                                                                       #"!nuke - удаление всего что можно (только для модераторов), "
                                                                                       "!exit - закрытие бота (только для стримера), "
                                                                                       #"!imba - узнать мнение бота о балансе в ск2, "
                                                                                       "!play - заказать музыку (принимаются видео с ютуба), "
                                                                                       "!queue - показать очередь заказанной музыки, "
                                                                                       "!points - показать количество пунтосов у пользователя, "
                                                                                       "!AOE4rank - показать ранг стримлера в таблице на ageofempires.com/ageiv",
                                                                               'hideIcon': False, 'mobile': False}}))
                    time.sleep(0.5)

                elif not boolhatred and messagelist["data"]["messages"][i]["text"][:len("!toxic ")].strip()=="!toxic" and messagelist["data"]["messages"][i]["user_id"] in modsids:
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': "начинаем хейтить пользователя: "+hated, 'hideIcon': False, 'mobile': False}}))
                    boolhatred=True
                    time.sleep(0.5)

                elif boolhatred and messagelist["data"]["messages"][i]["text"][:len("!stop ")].strip() == "!stop" and messagelist["data"]["messages"][i]["user_id"] in modsids:
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': "заканчиваем хейтить пользователя: " + hated,'hideIcon': False, 'mobile': False}}))
                    boolhatred = False
                    hatedDetected = False
                    time.sleep(0.5)

                elif messagelist["data"]["messages"][i]["text"][:len("!feed ")].strip() == "!feed" or messagelist["data"]["messages"][i]["text"][:len("!фид ")].strip() == "!фид":
                    laststuff["feedtime"]+=1
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': "этот нубас нафидил уже "+str(laststuff["feedtime"])+" раз.",'hideIcon': False, 'mobile': False}}))
                    time.sleep(0.5)

                elif messagelist["data"]["messages"][i]["text"][:len("!exit ")].strip() == "!exit" and messagelist["data"]["messages"][i]["user_id"] == 181773:
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': "Я устал я ухожу",'hideIcon': False, 'mobile': False}}))
                    stay_online = False
                    time.sleep(0.5)

                elif messagelist["data"]["messages"][i]["text"][:len("!trash ")].strip() == "!trash":
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': "Удаляю мусор.", 'hideIcon': False, 'mobile': False}}))
                    for j in range(len(messagelist["data"]["messages"])):
                        if messagelist["data"]["messages"][j]["user_name"] == hated:
                            g_socket.send(json.dumps({'type': "remove_message", 'data': {'channel_id': idchannel, 'message_id': messagelist["data"]["messages"][j]["message_id"]}}))
                            time.sleep(0.5)

                elif messagelist["data"]["messages"][i]["text"][:len("!nuke ")].strip() == "!nuke" and messagelist["data"]["messages"][i]["user_id"] in modsids:
                    g_socket.send(json.dumps({'type': "send_message",
                                              'data': {'channel_id': idchannel, 'text': "Обнаружен запуск ядерной ракеты.", 'hideIcon': False,
                                                       'mobile': False}}))
                    for j in range(len(messagelist["data"]["messages"])):
                        g_socket.send(json.dumps({'type': "remove_message", 'data': {'channel_id': idchannel, 'message_id': messagelist["data"]["messages"][j]["message_id"]}}))
                        time.sleep(0.1)

                elif messagelist["data"]["messages"][i]["text"][:len("!imba ")].strip()=="!imba":
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': "протоссы имба, когда их уже занерфят?", 'hideIcon': False, 'mobile': False}}))
                    time.sleep(0.5)

                elif messagelist["data"]["messages"][i]["text"][:len("!play ")].strip() == "!play":
                    p = 0
                    while p<len(messagelist["data"]["messages"][i]["text"]) and messagelist["data"]["messages"][i]["text"][p:p+len("https://")] != "https://" and messagelist["data"]["messages"][i]["text"][p:p+len("http://")] != "http://" and messagelist["data"]["messages"][i]["text"][p:p+len("www.")] != "www.":
                        p+=1
                    if p<len(messagelist["data"]["messages"][i]["text"]):
                      s = messagelist["data"]["messages"][i]["text"][p:len(messagelist["data"]["messages"][i]["text"])]
                      check = music.Add(s)
                      if check == 0:
                          g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                     'text': "Добавил ссылку в очередь.",
                                                                                     'hideIcon': False, 'mobile': False}}))
                      elif check == -1:
                          g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                     'text': "Непохоже на ссылку с youtube. :fuckoff: ",
                                                                                     'hideIcon': False, 'mobile': False}}))
                      elif check == -2:
                          g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                     'text': "Видео больше 15 минут не принимаю. :fuckoff: ",
                                                                                     'hideIcon': False, 'mobile': False}}))
                      elif check == -3:
                          g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                     'text': "Эту ссылку уже ранее добавляли.",
                                                                                     'hideIcon': False, 'mobile': False}}))
                      time.sleep(0.5)
                    else:
                        g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': messagelist["data"]["messages"][i]["user_name"]+", есть ссылка? А если найду? :fuckoff: ",
                                                                                   'hideIcon': False, 'mobile': False}}))
                        time.sleep(0.5)
                elif messagelist["data"]["messages"][i]["text"][:len("!queue ")].strip() == "!queue":
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                               'text': music.ShowQueue(),
                                                                               'hideIcon': False, 'mobile': False}}))
                    time.sleep(0.5)

                elif messagelist["data"]["messages"][i]["text"][:len("!points ")].strip() == "!points":
                    parsed = messagelist["data"]["messages"][i]["text"].split(" ")
                    if len(parsed) < 2:
                        g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': "Неправильное использование команды. :fuckoff:",
                                                                                   'hideIcon': False, 'mobile': False}}))
                    else:
                        curr_output = streamcurrency.LookupCurrency(parsed[1])
                        if curr_output == -1:
                            g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': "Пользователь "+parsed[1]+" ещё не получал пунтосов или его вовсе тут нет.",
                                                                                   'hideIcon': False, 'mobile': False}}))
                        else:
                            g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': "У пользователя " + parsed[
                                                                                       1] + " " + str(curr_output) + " пунтосов.",
                                                                                   'hideIcon': False, 'mobile': False}}))
                    time.sleep(0.5)

                elif messagelist["data"]["messages"][i]["text"][:len("!grant ")].strip() == "!grant":
                    if messagelist["data"]["messages"][i]["user_id"] not in modsids:
                        g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': messagelist["data"]["messages"][i]["user_name"] + ", у тебя нет прав на это. :fuckoff:",
                                                                                   'hideIcon': False, 'mobile': False}}))
                    else: #probably should have some exception catching here or manual error detection
                        parsed = messagelist["data"]["messages"][i]["text"].split(" ")
                        streamcurrency.GrantCurrency({"name": parsed[1]}, int(parsed[2]))
                        g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': "Пользователю " + parsed[1] + " добавлено " + parsed[2] + " пунтосов.",
                                                                                   'hideIcon': False, 'mobile': False}}))
                    time.sleep(0.5)


                elif messagelist["data"]["messages"][i]["text"][:len("!aoe4rank ")].strip().lower() == "!aoe4rank":
                    rank_r = requests.post("https://api.ageofempires.com/api/ageiv/Leaderboard",
                                           json = {"region": "7", "versus": "players", "matchType": "unranked", "teamSize": "1v1", "searchPlayer": "entrropical", "page": 1, "count":100},
                                           headers = {'Content-Type': 'application/json'})

                    if rank_r.status_code == 200:
                        parsed = json.loads(rank_r.content)['items'][0]
                        #print(parsed)
                        g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': "Игрок "+parsed["userName"]+" находится на позиции "+str(parsed["rank"])+" среди всех игроков Age of Empires 4, сыгравших 10 и более матчей. "
                                                                                    "ЭЛО: "+str(parsed["elo"])+", побед: "+str(parsed["wins"])+", поражений: "+str(parsed["losses"])+", винрейт: "+str(parsed["winPercent"])+"%.",
                                                                                   'hideIcon': False, 'mobile': False}}))
                    else:
                        g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel,
                                                                                   'text': "Не смог запросить результаты из таблицы рекордов age of empires 4, код ошибки на запрос: "+str(rank_r.status_code),
                                                                                   'hideIcon': False, 'mobile': False}}))


                    time.sleep(0.5)

                # extra message commands go here

            else:
                for j in range(len(messagelist["data"]["messages"][i]["text"]) - len(botlogin + ",")):
                    if messagelist["data"]["messages"][i]["text"][j:j+len(botlogin+",")] == botlogin+",":
                        rsp = False
                        for z in range(len(messagelist["data"]["messages"][i]["text"])):
                            if messagelist["data"]["messages"][i]["text"][z:z+len(":rock:")] == ":rock:" or messagelist["data"]["messages"][i]["text"][z:z+len(":paper:")] == ":paper:" or messagelist["data"]["messages"][i]["text"][z:z+len(":scissors:")] == ":scissors:":
                                rsp = True
                                g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': messagelist["data"]["messages"][i]["user_name"] + ", " + ":rsp:", 'hideIcon': False, 'mobile': False}}))
                        if not rsp:
                            g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': messagelist["data"]["messages"][i]["user_name"]+", "+botphrases[random.randrange(len(botphrases))], 'hideIcon': False, 'mobile': False}}))
                        tasks.addtime(30)
                        time.sleep(0.5)
                        break
        except Exception as e:
          log = open(os.path.dirname(os.path.realpath(__file__))+'\\errorlog.txt', 'a')
          log.write("["+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+"] error during message handling: "+str(e) + '\n')
          log.close()
        laststuff["timestamp"] = messagelist["data"]["messages"][len(messagelist["data"]["messages"])-1]["timestamp"]

        try:
         for i in range(len(userlist["data"]["users"])):
            #connector to streamcurrency:
            curr_amount = 1
            #type(userlist["data"]["users"][i]["id"]) is str
            if int(userlist["data"]["users"][i]["id"]) in modsids: curr_amount = 3 #simple way to give mods more curr
            tasks.addtask({"type": "grantcurr",
                           "content": {"user" : userlist["data"]["users"][i], "amount" : curr_amount },
                           "time": time.time()+60})
            #old part:
            if boolhatred and userlist["data"]["users"][i]['name'] == hated:
                if not hatedDetected:
                    hatedDetected=True
                    g_socket.send(json.dumps({'type': "send_message", 'data': {'channel_id': idchannel, 'text': userlist["data"]["users"][i]['name'] + emptystr +" найден. Вот ты и попался!", 'hideIcon': False, 'mobile': False}}))
                    emptystr = " снова "
                    tasks.addtask({"type": "hatemsg",
                              "content": hated+", :fuckoff:",
                              "id" : userlist["data"]["users"][i]["id"],
                              "time": time.time()+10})
            elif userlist["data"]["users"][i]['name'] not in {'ToxicBot', 'Entropical'} and userlist["data"]["users"][i]['name'] not in greeted:
                tasks.addtask({"type": "greeting",
                               "content": userlist["data"]["users"][i]['name'] + ", " + botwelcome[random.randrange(len(botwelcome))],
                               "time": time.time()+5})
                greeted.add(userlist["data"]["users"][i]['name'])
        except Exception as e:
            log = open(os.path.dirname(os.path.realpath(__file__)) + '\\errorlog.txt', 'a')
            log.write("[" + time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(time.time())) + "] error during user list check: " + str(e) + '\n')
            log.close()
        time.sleep(1)
    except Exception as e:
        log = open(os.path.dirname(os.path.realpath(__file__))+'\\errorlog.txt', 'a')
        log.write("["+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+"] error during main cycle (unclear which process): "+str(e) + '\n')
        log.close()
    #--------------------------------------------------------------------------------------------------------------
    #maybe add saving to file as a task every 5 minutes or something
    writestuff = open(os.path.dirname(os.path.realpath(__file__))+'\\botdata.txt', 'w')
    writestuff.write(json.dumps(laststuff))
    writestuff.close()
    streamcurrency.SaveIntoFile()

    print("toxicbot endedn?")
    print(stay_online)

    """ this deletes bot messages. For beta-testing.
    g_socket.send(json.dumps({'type': "get_channel_history", 'data': {'channel_id': idchannel, 'hidden': True}}))
    time.sleep(0.5)
    m_list=json.loads(g_socket.recv())
    deletelist = list()
    print(m_list)
    fuckingdoit = False
    while not fuckingdoit:
     try:
      for i in range(len(m_list["data"]["messages"])):
        if m_list["data"]["messages"][i]["user_name"]=='ToxicBot':
            deletelist.append(m_list["data"]["messages"][i]["message_id"])
     except:
         print("FUCK ME")
         m_list = json.loads(g_socket.recv())
     else:
         fuckingdoit = True
    
    if len(deletelist)>0:
        g_socket.send(json.dumps({'type': "send_message",
                                  'data': {'channel_id': "166776", 'text': "удаляю мусор",
                                           'hideIcon': False,
                                           'mobile': False}}))
    for i in range(len(deletelist)):
        g_socket.send(json.dumps({'type': "remove_message", 'data': {'channel_id': idchannel, 'message_id': deletelist[i]}}))
        time.sleep(0.5)
    g_socket.send(json.dumps({'type': "unjoin", 'data': {'channel_id': idchannel, 'hidden': True}}))
    """
    g_socket.send(json.dumps({'type': "unjoin", 'data': {'channel_id': idchannel, 'hidden': True}}))
    time.sleep(1)
    g_socket.close()

if __name__ == "__main__":
    invoke(None)