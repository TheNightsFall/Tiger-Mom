import dns
import os
import pymongo
from discord.ext import tasks, commands
import discord.utils
import datetime
from datetime import timedelta
import asyncio
import pytz

cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]
channel = ""
messageSend = ""
class Practice(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(brief = "Log practice time.", description = "Log practice minutes and accomplishments.")
  async def log(self, ctx, amountPracticed = None, *args):
    if amountPracticed == None:
      await ctx.send("WHAT? No practice? I mapo your tofu tonight!")
    elif amountPracticed.isnumeric() == False:
      await ctx.send("Practice time must be a number lah!")
    else:
      user = getUserData(ctx.author.id)
      minutes = user["practiceTime"]
      utcNow = pytz.utc.localize(datetime.datetime.utcnow())
      timeNow = utcNow.strftime("%d %b %Y")
      minutes += int(amountPracticed) if minutes != None else int(amountPracticed)
      repertoire = ""
      for x in args:
        repertoire += x
        repertoire += " "
      repertoire = repertoire[:-1]
      
      Value = str(amountPracticed)+ " " +repertoire
      userData.update_one({"id":ctx.author.id}, {"$set": {"practiceTime": minutes}})
      userData.update_one({"id":ctx.author.id}, {"$push":{"practiceLog": {timeNow: Value}}})
      await ctx.send("Updated lah! Keep practicing or I kungpao your chicken!")
    
  @commands.command(aliases = ["setpracticegoals", "setgoals"], brief = "Set practice goals.", description = "Set practice goals.")
  async def setgoal(self, ctx, *args):
    goal = ""
    for x in args:
      goal += x
      goal += " "
    goal = goal[:-1]
    if goal is None:
      await ctx.send("You need to specify a goal lah!")
    else:
      user = getUserData(ctx.author.id) #Makes sure user in database
      goalMatch = userData.find_one({"id": ctx.author.id, "to-do": goal})
      if goalMatch is None:
        userData.update_one({"id": ctx.author.id}, {"$push": {"to-do": goal}})
        await ctx.send("Added goal "+goal)
      else:
        await ctx.send("Goal already exists lah!")

  #got to do error-checking for this lol
  @commands.command(brief="Set a reminder.", description = "Set a reminder.")
  async def reminder(self, ctx, reminder = None, timeTil = None):
    global channel
    global messageSend
    reminder = "Go practice lah!" if reminder is None else reminder
    timeTil = 5 if timeTil is None else timeTil 
    messageSend = reminder
    channel = discord.utils.get(ctx.guild.channels, name=str(ctx.channel))
    channel = channel.id
    why.start(self.bot, timeTil)



def getUserData(x):
  userTeam = userData.find_one({"id": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "streak": 0, "to-do": [], "practiceLog": [],"sprintRemaining": -10, "dailyLastCollected": d, "practiceGoal": 0}
    userData.insert_one(newUser)
  userTeam = userData.find_one({"id": x})
  return userTeam 

@tasks.loop()
async def why(bot, timeSleep):
  global channel
  global messageSend
  while True:
    print(channel)
    chanel = bot.get_channel(channel)
    await chanel.send(messageSend)
    await asyncio.sleep(timeSleep)


def setup(bot):
  bot.add_cog(Practice(bot))