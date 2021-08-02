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
from pretty_help import PrettyHelp, DefaultMenu
from keep_alive import keep_alive
#from cogs import bubbletea
#For color conversions to decimal: https://convertingcolors.com/
#kill 1 in shell if rate limited


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.voice_states = True

cluster = pymongo.MongoClient(os.getenv('THING'))
guildData = cluster["tigermom"]["guilds"]
teamData = cluster["tigermom"]["teams"]
bot = commands.Bot(command_prefix="p.", 
case_insensitive=True, 
intents=intents, 
description = "Keep practicing lah!")

nav = DefaultMenu(page_left="🔼", page_right="🔽")
bot.help_command = PrettyHelp(navigation = nav, color=16092072, active_time=40)

@bot.event
async def on_ready():
  print('Logged in as {0.user}. Get practicing lah!'.format(bot))
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" you practice | p.help"))
  #guildData.update_many({}, {"$set": {"queuelink": []}})
  #guildData.update_many({}, {"$set": {"queue": []}})
  checkDate.start()
  checkChal.start()

@bot.event
async def on_message(message):
  if message.author == bot.user:
    pass
  elif "interesting" in message.content.lower():
    await message.add_reaction(r'<:eddy_interesting:760913535013748746>')
  elif "amazing" in message.content.lower():
    await message.add_reaction(r'<:amazing:862390230429335562>')
  await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, CommandNotFound):
    await ctx.send("Command doesn't exist lah!")
  elif isinstance(error, commands.CommandOnCooldown):
    pass
  elif isinstance(error, discord.Forbidden):
    await ctx.send("I don't have permission to run this command.")
  else:
    await ctx.send(f"{error}. Blame nights, she terrible at coding. No wonder she no doctor lah.")
    raise error

@tasks.loop(seconds = 10) # Changes status upon a TS Bday
async def checkDate():
  while True:
    utcNow = pytz.utc.localize(datetime.datetime.utcnow())
    timeNow = utcNow.strftime("%d %b")
    if timeNow == "23 Mar":
      await bot.change_presence(activity=discord.Activity (type=discord.ActivityType.playing, name="Happy Birthday Eddy! | p.help"))
    elif timeNow == "3 Mar":
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Happy Birthday Brett! | p.help"))
    else:
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" you practice | p.help"))
    await asyncio.sleep(5)

@tasks.loop(minutes = 1)
async def checkChal():
  while True:
    current = datetime.datetime.now()
    no = list(teamData.find({"accepted": {"$type": "array", "$ne": []}}))
    loop = -1
    for x in no:
      loop += 1
      timeChal = datetime.datetime.strptime(no[loop]["accepted"][0]["expiration"], "%m/%d/%Y %H:%M:%S")
      if current >= timeChal:
        bal1 = no[loop]["accepted"][0]["bal"]
        t1 = teamData.find_one({"tn": no[loop]["tn"]})
        t2 = teamData.find_one({"tn": no[loop]["accepted"][0]["challenged"]})
        capt1 = t1["captains"]
        capt2 = t2["captains"]
        try:
          bal2 = t2["accepted"][0]["bal"]
          name1 = t1["tn"]
          name2 = t2["tn"]
          if bal1 == bal2:
            if bal1 == 0:
              xp1 = xp2 = 0
              em1 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name1}! Your challenge against team {name2} has ended. Neither of you made any bubble tea. No xp rewarded.", color =	15417396)
              em2 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name2}! Your challenge against team {name1} has ended. Neither of you made any bubble tea. No xp rewarded.", color =	15417396)
            else:
              xp1 = xp2 = 2
              em1 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name1}! Your challenge against team {name2} has ended. You both tied, making {bal1}. You both gain 2 xp.", color =	15417396)
              em2 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name2}! Your challenge against team {name1} has ended. You both tied, making {bal1}. You both gain 2 xp.", color =	15417396)
          elif bal1 < bal2:
            xp1 = 0
            xp2 = 4
            em1 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name1}! Your challenge against team {name2} has ended. You lost, {bal1} against {bal2}. Your team gains nothing.", color =	15417396)
            em2 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name2}! Your challenge against team {name1} has ended. You won, {bal2} against {bal1}. Your team gains 4 xp.", color =	15417396)
          else:
            xp1 = 4
            xp2 = 0
            em2 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name2}! Your challenge against team {name1} has ended. You lost, {bal2} against {bal1}. Your team gains nothing.", color =	15417396)
            em1 = discord.Embed(title = "ATTENTION! CHALLENGE ENDED!", description = f"Hello, captains of {name1}! Your challenge against team {name2} has ended. You won, {bal1} against {bal2}. Your team gains 4 xp.", color =	15417396)
          teamData.update_one({"tn": name1}, {"$pull": {"accepted": {"expiration": no[loop]["accepted"][0]["expiration"], "challenged": name2, "bal": bal1}}})
          teamData.update_one({"tn": name2}, {"$pull": {"accepted": {"expiration": no[loop]["accepted"][0]["expiration"], "challenged": name1, "bal": bal2}}})
          teamData.update_one({"tn":name1}, {"$inc": {"xp": xp1}})
          teamData.update_one({"tn":name2}, {"$inc": {"xp": xp2}})
          for captain in capt1:
              check = bot.get_user(int(captain))
              channel = await check.create_dm()
              await channel.send(embed = em1)
          for captain in capt2:
              check = bot.get_user(int(captain))
              channel = await check.create_dm()
              await channel.send(embed = em2)
        except:
          pass
    await asyncio.sleep(50)

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
