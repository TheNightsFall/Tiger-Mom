import dns
import os
import pymongo
from discord.ext import commands
import discord.utils
import datetime
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
      
      Value = str(amountPracticed)+ " " +repertoire if repertoire != "" else str(amountPracticed)
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
    if goal == "":
      await ctx.send("You need to specify a goal lah!")
    else:
      user = getUserData(ctx.author.id) #Makes sure user in database
      goalMatch = userData.find_one({"id": ctx.author.id, "to-do": goal})
      if goalMatch is None:
        userData.update_one({"id": ctx.author.id}, {"$push": {"to-do": goal}})
        await ctx.send("Added goal "+goal)
        goal += " gs" #Goal set.
        #userData.update_one({"id":ctx.author.id}, {"$push":{"practiceLog": {timeNow: goal}}})
      else:
        await ctx.send("Goal already exists lah!")

  @commands.command(brief = "Displays active goals.", description = "Displays active goals.")
  async def goals(self, ctx):
    user = getUserData(ctx.author.id)
    items = user["to-do"]
    em = discord.Embed(title = f"{ctx.author.display_name}'s Goals", color = 16092072)
    em.set_thumbnail(url=ctx.author.avatar_url)
    for item in items:
      if item.find(",") == -1:
        em.add_field(name = item, value = "[no desc added]") #Ugly af I know but can't think of anything else
      else:
        x = item.split(",", 1)
        em.add_field(name = x[0], value = x[1])
    em.set_footer(text="Go practice lah!")
    await ctx.send(embed = em)

  @commands.command(aliases = ["delete", "dg"], brief = "Delete a goal.", description = "Delete a goal.")
  async def deletegoal(self, ctx, *args):
    user = getUserData(ctx.author.id)
    items = user["to-do"]
    goal = ""
    for x in args:
      goal += x
      goal += " "
    goal = goal[:-1]
    if goal == "":
      await ctx.send("You need to specify a goal to delete lah!")
      return
    match = 0
    for item in items:
      if item.find(",") == -1:
        if item.lower() == goal.lower():
          userData.update({"id": ctx.author.id}, {"$pull": {"to-do": goal}})
          match = 1
      else:
        x = item.split(",", 1)
        Item = x[0]
        if Item.lower() == goal.lower():
          userData.update({"id": ctx.author.id}, {"$pull": {"to-do": item}})
          match = 1
    if match == 1:
      await ctx.send(f"Goal {goal} deleted!")
    else:
      await ctx.send("Goal doesn't exist lah!")
  
  @commands.command(aliases = ["finishgoal", "mg"], brief = "Mark a goal as finished.", description = "Mark a goal as finished.")
  async def meetgoal(self, ctx, *args):
    user = getUserData(ctx.author.id)
    items = user["to-do"]
    goal = ""
    for x in args:
      goal += x
      goal += " "
    goal = goal[:-1]
    if goal == "":
      await ctx.send("You need to specify a goal to complete lah!")
      return
    match = 0
    for item in items:
      if item.find(",") == -1:
        if item.lower() == goal.lower():
          userData.update({"id": ctx.author.id}, {"$pull": {"to-do": goal}})
          userData.update_one({"id": ctx.author.id}, {"$push": {"to-done": goal}})
          match = 1
      else:
        x = item.split(",", 1)
        Item = x[0]
        if Item.lower() == goal.lower():
          userData.update({"id": ctx.author.id}, {"$pull": {"to-do": item}})
          userData.update_one({"id": ctx.author.id}, {"$push": {"to-done": item}})
          match = 1
    if match == 1:
      await ctx.send(f"Goal {goal} completed!")
    else:
      await ctx.send("Goal doesn't exist lah!")

  @commands.command(aliases = ["fg"], brief = "Displays active goals.", description = "Displays active goals.")
  async def finishedgoals(self, ctx):
    user = getUserData(ctx.author.id)
    items = user["to-done"]
    em = discord.Embed(title = f"{ctx.author.display_name}'s Finished Goals", color = 16092072)
    em.set_thumbnail(url=ctx.author.avatar_url)
    for item in items:
      if item.find(",") == -1:
        em.add_field(name = item, value = "[no desc added]")
      else:
        x = item.split(",", 1)
        em.add_field(name = x[0], value = x[1])
    em.set_footer(text="Go practice lah!")
    await ctx.send(embed = em)

def getUserData(x):
  userTeam = userData.find_one({"id": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "streak": 0, "to-do": [], "practiceLog": [],"sprintRemaining": -10, "dailyLastCollected": d, "practiceGoal": 0, "to-done": []}
    userData.insert_one(newUser)
  userTeam = userData.find_one({"id": x})
  return userTeam 

def setup(bot):
  bot.add_cog(Practice(bot))

'''
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

@tasks.loop()
async def why(bot, timeSleep):
  global channel
  global messageSendwhile True:
  print(channel)
  chanel = bot.get_channel(channel)
  await chanel.send(messageSend)
  await asyncio.sleep(timeSleep)
'''