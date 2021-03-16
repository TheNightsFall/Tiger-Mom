import discord
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound
from os import listdir
from os.path import isfile, join
import os
import datetime
import pytz
import asyncio
#from cogs import bubbletea -- Not needed but just in case I forget how later
#For color conversions to decimal: https://convertingcolors.com/

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.voice_states = True

bot = commands.Bot(command_prefix="p.", 
case_insensitive=True, 
intents=intents, 
description = "Keep practicing lah!")
bot.remove_command('help')

@bot.event
async def on_ready():
  print('Logged in as {0.user}. Get practicing lah!'.format(bot))
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" you practice"))
  checkDate.start()

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, CommandNotFound):
    await ctx.send("Command doesn't exist lah!")
  else:
    raise error

@tasks.loop(seconds = 10) # Will change this to detect the date lol
async def checkDate():
  while True:
    utcNow = pytz.utc.localize(datetime.datetime.utcnow())
    timeNow = utcNow.strftime("%d %b")
    if timeNow == "23 Mar":
      await bot.change_presence(activity=discord.Activity (type=discord.ActivityType.playing, name="Happy Birthday Eddy!"))
    elif timeNow == "3 Mar":
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Happy Birthday Brett!"))
    else:
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" you practice"))
    await asyncio.sleep(5)

if __name__ == "__main__":
  for extension in [f.replace('.py', '') for f in listdir("cogs") if isfile(join("cogs", f))]:
    try:
      bot.load_extension("cogs" + "." + extension)
      #You can comment these print statements out, they're just useful bc if there are major errors within them, the cogs fail to load.
      print(f"Cog {extension} successfully loaded.")
    except:
      print(f"Failed to load extension {extension}. If you do surgery like you load cog, patient already dead.")
else:
  print("Something went wrong.")

bot.run(os.getenv('40HRS'))