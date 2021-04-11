import discord
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound
from os import listdir
from os.path import isfile, join
import os
import datetime
import pytz
import asyncio
import dns
import pymongo
from pretty_help import PrettyHelp, Navigation
from keep_alive import keep_alive
#from cogs import bubbletea
#For color conversions to decimal: https://convertingcolors.com/

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.voice_states = True

cluster = pymongo.MongoClient(os.getenv('THING'))
guildData = cluster["tigermom"]["guilds"]
bot = commands.Bot(command_prefix="p.", 
case_insensitive=True, 
intents=intents, 
description = "Keep practicing lah!")

nav = Navigation("🔼", "🔽")
bot.help_command = PrettyHelp(navigation = nav, color=16092072, active_time=40)


@bot.event
async def on_ready():
  print('Logged in as {0.user}. Get practicing lah!'.format(bot))
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" you practice"))
  #guildData.update_many({}, {"$set": {"queuelink": []}})
  #guildData.update_many({}, {"$set": {"queue": []}})
  checkDate.start()

@bot.event
async def on_message(message):
  if message.author == bot.user:
    pass
  elif "interesting" in message.content.lower():
    await message.add_reaction(r'<:eddy_interesting:760913535013748746>')
  await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, CommandNotFound):
    await ctx.send("Command doesn't exist lah!")
  elif isinstance(error, commands.CommandOnCooldown):
    pass
  else:
    raise error

@tasks.loop(seconds = 10) # Changes status upon a TS Bday
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
      #You can comment these print statements out, they're just useful to me bc if there are major errors they fail to load.
      print(f"Cog {extension} successfully loaded.")
    except:
      print(f"Failed to load extension {extension}. If you do surgery like you load cog, patient already dead.")
else:
  print("Something went wrong.")

keep_alive()
bot.run(os.getenv('40HRS'))