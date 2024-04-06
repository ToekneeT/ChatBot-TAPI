import config
from twitchio.ext import commands
from collections import defaultdict
from random import randint, uniform
import asyncio
import webbrowser

#DEBUG = False
DEBUG = True

# Sets value to 0 if not already in dictionary.
# Will be the commands sent in by the users.
# If it hits a threshold set in echo_command_on_threshold,
# it'll echo the command into chat.
# Gets reset every minute, only want to echo commands
# that are spammed within a short period of time.
# That way, it's not just spamming every single command being used.
chat_commands = defaultdict(lambda: 0)
# Will keep track of the commands used in chat by the
# bot throughout the stream. Used to output to a file.
commands_used = defaultdict(lambda: 0)
# Some global variables to have the bot do different things.
extra_shop = False
is_buy_from_shop = False
sub_cooldown = False
is_echo_command = False
is_send_reaction_to_sub = True
is_buy_from_extra_shop = False


async def sub_reaction_sleep(sleep_time):
    global is_send_reaction_to_sub
    await asyncio.sleep(sleep_time)
    is_send_reaction_to_sub = False

# Clears the chat_commands every minute
# That way the commands need to be spammed
# in order for it to be echoed.
async def clear_chat_commands():
    global chat_commands
    while True:
        await asyncio.sleep(60)
        chat_commands.clear()


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=config.OAUTH_TOKEN, prefix='?', initial_channels=config.CHANNELS if not DEBUG else config.DEBUG_CHANNEL)

        # refresh token: x
        # client id: x

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        print(f'Connected channels  | {bot.connected_channels}')
        # Opens the chat where bot controls will be done on.
        webbrowser.open_new(config.CMD_CHAT)
        await clear_chat_commands()

    # Reads input from another channel to control the bot.
    async def command_input(self, author, message):
        global extra_shop
        global is_buy_from_shop
        global sub_cooldown
        global is_echo_command
        global is_send_reaction_to_sub
        global is_buy_from_extra_shop
        message = message.lower()

        if author == config.USERNAME and context.channel.name == config.CHANNELS[1]:
            if message in ['shop on', 'on']:
                print('----- Buying from shop is on! -----')
                is_buy_from_shop = True
            elif message.split()[0] == "deposit":
                extra_shop = message.split()[1]
                print('----- Buying shop item {extra_shop}! -----')
                is_buy_from_extra_shop = True
            elif message in ['shop off', 'off']:
                print('----- Buying from shop is off! -----')
                is_buy_from_shop = False
            elif message in ['event', 'event on', 'eon']:
                print('----- Event command is on! -----')
                is_echo_command = True
            elif message in ['event off', 'eoff']:
                print('----- Event command is off! -----')
                is_echo_command = False
            elif message in ['limit', 'limit on', 'lon']:
                print('----- Sub cooldown limit on! -----')
                is_cooldown_limit = True
            elif message in ['status', 's']:
                print('---------- Status ----------')
                print(f'----- Buying from Shop: {is_buy_from_shop} -----')
                if is_buy_from_extra_shop:
                    print(f'----- Buying shop slot {extra_shop}! -----')
                print(f'----- Event Command: {is_echo_command} -----')
                #print(f'----- Sub cooldown limit: {is_cooldown_limit} -----')
                print(f'----- Sending Sub Reaction: {is_send_reaction_to_sub} -----')
            # Sets a timer to stop sending sub reactions. In case I don't want it running the entire night.
            elif message.split()[0] == 'sleep':
                print(f'-----Sleeping in {message.split()[1]} seconds.-----')
                await sub_reaction_sleep(int(message.split()[1]))
            elif message in ['son', 'sub on']:
                is_send_reaction_to_sub = True
                print('----- Sub reaction on! -----')
            elif message in ['commands', 'cmd']:
                # Will write to a file with how many of each command was used
                # during the runtime of the bot.
                file = open('commands.csv', 'w')
                for key in commands_used:
                    file.write(f'{key},{commands_used[key]}\n')
                file.close()
            else:
                print("---------- Invalid Input ----------")

    # Echoes a command into chat once a threshold (100) has been reached.
    # Resets the command iteration back to 0 once it echoes.
    async def echo_command_on_threshold(self, message):
        global chat_commands
        global commands_used
        # Once the number hits 100, bot will echo command into chat.
        if chat_commands[message] >= 100 and is_echo_command:
            await bot.connected_channels[0].send(message)
            # Sets that command iteration back to 0 once it echos the command
            # in order to prevent it from being spammed
            chat_commands[message] = 0
            commands_used[message] += 1

    # If a message starts with !, it'll increment a count variable in a dictionary.
    async def increment_commands(self, message):
        global chat_commands
        # Don't want to read !no or !yes as the dictionary controls what gets echoed.
        # Don't want to echo them as it can make a bet or make the wrong bet.
        if message[0] == "!" and message.lower() != '!no' and message.lower() != '!yes':
            chat_commands[message] += 1

    # When someone subscribes, an external bot (target_user) will send a message.
    # The bot will then respond by sending an random amount of an emote
    # from a range of 1 to 5 to give variety and decrease the chance it'll
    # send the same message twice.
    async def sub_event(self, author, message):
        target_user = config.TARGET_USER[0] if not DEBUG else config.DEBUG_CHANNEL[0]
        if author == target_user and message[0] == "⭐" and is_send_reaction_to_sub:
            await asyncio.sleep(round(uniform(2, 5), 1))
            await bot.connected_channels[0].send('dnkM ' * randint(1, 5))
            #await self.handle_commands(context.message)
            await asyncio.sleep(round(uniform(5, 10), 1))
            commands_used["Sub Reaction"] += 1

    # Buys shop item depending on a specific user and specific input.
    async def buy_shop(self, author, message):
        global extra_shop
        global is_buy_from_shop
        global is_buy_from_extra_shop
        global commands_used
        target_user = config.TARGET_USER[1] if not DEBUG else config.DEBUG_CHANNEL[0]
        # Message needs to be the from an external bot, otherwise ignore.
        # Needs to be buying something, otherwise ignore.
        if author != target_user or not (is_buy_from_shop or is_buy_from_extra_shop):
            return
        # Checks if the external bot has sent a specific message, otherwise ignore.
        if message != 'The market is now open!':
            return
        # Different timers depending on which item slot it's going to buy
        # Don't want it to buy an item too fast and be too suspicious.
        # But also want to buy it fast enough the stock doesn't sell out.
        # Different delays depending on if it's buying from another shop slot.
        # The stock on extra slots are typically lower, so if there's an extra slot,
        # we want to prioritize that first before the first slot.
        if is_buy_from_shop:
            await asyncio.sleep(1.5 if is_buy_from_shop else 0.5)
            await bot.connected_channels[0].send('!deposit 1')
            commands_used['!deposit 1'] += 1
        elif is_buy_from_extra_shop and not is_buy_from_shop:
            await asyncio.sleep(0.5)
            await bot.connected_channels[0].send(f'!deposit {extra_shop}')
            is_buy_from_extra_shop = False
            commands_used[f'!deposit {extra_shop}'] += 1
        elif is_buy_from_shop and is_buy_from_extra_shop:
            await asyncio.sleep(0.5)
            await bot.connected_channels[0].send(f'!deposit {extra_shop}')
            await asyncio.sleep(1.5)
            await bot.connected_channels[0].send('!deposit 1')
            is_buy_from_extra_shop = False
            commands_used[f"!deposit 1"] += 1
            commands_used[f"!deposit {extra_shop}"] += 1
        is_buy_from_shop = False

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        context = await self.get_context(message)
        author = context.author.name

        # Print the contents of our message to console...
        # Formatted so that all messages start 17 (arbitrary) characters in.
        # Splice the username if it's too long.
        print('{: <17} : {}'.format(context.author.name[:17], message.content))

        await self.increment_commands(message.content)
        await self.command_input(author, message.content)
        await self.echo_command_on_threshold(message.content)
        await self.sub_event(author, message.content)
        await self.buy_shop(author, message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)


bot = Bot()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
bot.run()


print("----- Bye-bye! -----")