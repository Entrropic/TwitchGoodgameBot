# TwitchGoodgameBot
My little bot I did in my spare time as a hobby. The code is probably pretty horrendous, but suits my needs. Current functionality includes: 
1. Common "launcher" for goodgame+twitch components
2. Ability to play music (using pafy) with common music queue for both goodgame and twitch components
3. A few misc chat functions

Structure:

Launcher.py - the launcher file, includes Twitch, Goodgame and musicplaying components

GGBot.py - Goodgame component.

TwitchBot.py - Twitch component.

YoutubeVideoTest.py - musicplaying component (uses pafy)

StreamCurrencyManager.py - unfinished "stream currency" component, only works for goodgame right now.

Русский перевод:

Мой небольшой бот, который я делал в свободное время в качестве хобби. Это один из первых проектов, поэтому спроектировано не самым лучшим образом, но поставленную задачу он выполнял. Функционал бота:
1. Общий "лаунчер", который запускает компоненты для goodgame.ru и twitch.tv
2. Возможность играть музыку, используя библиотеку pafy, с общей музыкальной очередью для твича и гудгейма
3. Несколько других небольших функций для чата

Структура:

Launcher.py - общий лаунчер, через него запускаются компоненты для твича, гудгейма и для проигрывания музыки

GGBot.py - компонент для гудгейма

TwitchBot.py - компонент для твича

YoutubeVideoTest.py - компонент для проигрывания музыки, использует pafy

StreamCurrencyManager.py - не до конца доделанный компонент "валюты для стрима" (валюта, которая даётся за просмотр стрима, аналогично тому, что можно увидеть на каналах на том же твиче). Работает только для гудгейма.
