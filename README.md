# ChatBot-TAPI
Chatbot that was moved over to use Twitchio api.

## What does it do?
The bot is very niche and was created to do tasks very specifically for me for a very specific streamer that I watch.
This streamer has rewards (currency) when reacting to someone subscribing to the channel as well as a cosmetic for a channel specific character.
The cosmetic is sold in a shop that is open a few times per stream and has a stock that can be sold out if too many people are buying it.
In order to farm the currency as well as purchase these items for me, I have created this bot.
The streamer also does event streams when he reaches a milestone in a game, to which the stream doesn't end until he beats the challenge that he sets for himself.
There's always a special cosmetic for these events, but it's only released when he completes the challenge.
There have been times the stream has run for over 24 hours and I have missed the cosmetic.
To counteract that, I have the bot echo commands that are spammed in the chat.

I don't recommend this bot as again, it's very niche and very specific to a channel; however, if you still want to run it, I will list the instructions below.

## How to run
In order to run, you'll need a few libraries.
The first library is the main driving force of the bot.

Python 3.7+

`pip install twitchio`

[Twitchio](https://twitchio.dev/en/stable/)

You'll also need Asyncio as it's used for timers within the bot.

`pip install asyncio`

### config file
In order for the bot to run, you'll need a `config.py` file. The file is imported by the bot and is what's used to check which channels it'll monitor as well as where you put your oauth token.

You can find your [OAUTH token here](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/)

The format of the config file is:

`OAUTH_TOKEN = '<token here>'
CHANNELS = ['<twitch channel(s)>']
DEBUG_CHANNEL = ['<a debug channel if you want to test.>']
TARGET_USER = ['<target users>]`