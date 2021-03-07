import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from os import listdir
from os.path import isfile, join
import os
import datetime
#For color conversions to decimal: https://convertingcolors.com/

intents = discord.Intents.none()
intents.members = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.voice_states = True

bot = commands.Bot(command_prefix="p.", 
case_insensitive=True, 
intents=intents, 
description = "Keep practicing lah!")

@bot.event
async def on_ready():
  print('Logged in as {0.user}. Get practicing lah!'.format(bot))
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" you practice"))

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, CommandNotFound):
    await ctx.send("Command doesn't exist lah!")
  else:
    raise error

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