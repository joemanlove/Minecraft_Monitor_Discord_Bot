# settings should have prefix and token variables
from bot_settings import prefix, token, channel_id

# import the math library
import math
# import discord python library
import discord
# import the command module
from discord.ext import commands

import asyncio

import os
DIRECTORY_PATH = os.path.dirname(__file__)

FILE_PATH = os.path.join(DIRECTORY_PATH, "logs/latest.log")

# Remind console user of the prefix
print(f'Attempting to launch Bot using {prefix} as the command prefix.')

# initialize discord client
bot = discord.Client()

# set command prefix
bot = commands.Bot(command_prefix=prefix)

# store the last line form the log
last_line = ''


def get_printables(log_contents):
    printables = ''
    for line in log_contents:
        if line.find('<') == -1 and line.find('[Server thread/INFO]:') > -1 and line.find('[/') == -1:
            printables += line.replace('[Server thread/INFO]:', '')
    return printables


def check_log_updates():
    global last_line

    server_log_stream = open(FILE_PATH, 'r')
    log_contents = server_log_stream.readlines()
    server_log_stream.close()

    try:
        i = log_contents.index(last_line)
    except ValueError:
        i = 0

    new_log_contents = log_contents[i+1:]

    if new_log_contents:
        message = get_printables(new_log_contents)
        last_line = new_log_contents[-1]
    else:
        message = ''

    return message


# if the bot is ready print that out.
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    # initialize last_line
    check_log_updates()
    bot.minecraft_log_channel = bot.get_channel(channel_id)
    bot.loop.create_task(status_task())


# ping command for testing purposes
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')


@bot.command(name='server_log')
async def server_log(ctx):

    message = check_log_updates()

    if message:
        await ctx.send(message)
    else:
        await ctx.send('No new updates to the server log.')


@bot.command(name='set_channel')
async def set_channel(ctx):
    bot.minecraft_log_channel = ctx.channel


# timer code from
# https://stackoverflow.com/questions/46267705/making-a-discord-bot-change-playing-status-every-10-seconds
async def status_task():
    while True:
        if bot.minecraft_log_channel:
            message = check_log_updates()

            if message:
                await bot.minecraft_log_channel.send(message)

        await asyncio.sleep(60)


bot.run(token)
