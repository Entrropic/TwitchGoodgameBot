# TwitchGoodgameBot
My little bot I did in my spare time as a hobby. The code is probably pretty horrendous, but suits my needs. Current functionality includes: 
1. Common "launcher" for goodgame+twitch components (needs fine-tuning)
2. Ability to play music (using pafy) with common music queue for both goodgame and twitch components
3. A few misc chat functions

Structure:

Launcher.py - the launcher file, includes Twitch, Goodgame and musicplaying components

GGBot.py - Goodgame component.

TwitchBot.py - Twitch component.

YoutubeVideoTest.py - musicplaying component (uses pafy)

StreamCurrencyManager - unfinished "stream currency" component, only works for goodgame right now.
