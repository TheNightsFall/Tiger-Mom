import dns
import os
import pymongo
from discord.ext import commands
import discord.utils
import datetime
from datetime import timedelta
import asyncio
import pytz
import random

cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]

#channel = ""
#messageSend = ""
#Stats leaderboard?, sprint
#colors: 16092072, 15417396

class Practice(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(brief = "Log practice time.", description = "Log practice minutes and accomplishments.")
  async def log(self, ctx, amountPracticed = None, *args):
    if amountPracticed == None:
      await ctx.send("WHAT? No practice? I mapo your tofu tonight!")
      return
    elif amountPracticed.isnumeric() == False:
      await ctx.send("Practice time must be a number lah!")
      return
    elif amountPracticed == 0:
      await ctx.send("Practice time cannot be zero lah!")
      return
    user = getUserData(ctx.author.id)
    minutes = user["practiceTime"]
    pract = user["practiceLog"]
    utcNow = pytz.utc.localize(datetime.datetime.utcnow())
    oneWeek = datetime.datetime.utcnow() - timedelta(days=8)
    timeNow = utcNow.strftime("%d %b %Y")
    minutes += int(amountPracticed) if minutes != None else int(amountPracticed)
    repertoire = ""
    for x in args:
      repertoire += x
      repertoire += " "
    repertoire = repertoire[:-1]
    userData.update_one({"id":ctx.author.id}, {"$set": {"practiceTime": minutes}})
    while len(pract) > 99:
      userData.update_one({"id": ctx.author.id}, {"$pull": {"practiceLog": {"date": pract[0]["date"], "minutes": pract[0]["minutes"]}}})
    pract = user["practiceLog"]
    if repertoire != "":
      Value = str(amountPracticed)+ " " +repertoire
      userData.update_one({"id":ctx.author.id}, {"$push":{"practiceLog": {"date": timeNow,"minutes": Value}}})
    else:
      loop = -1
      Value = str(amountPracticed)
      for x in pract:
        loop += 1
        try:
          if pract[loop]["date"] == timeNow:
            amountPracticed = int(pract[loop]["minutes"]) + int(amountPracticed)
            userData.update({"id": ctx.author.id}, {"$pull": {"practiceLog": {"date": timeNow, "minutes": pract[loop]["minutes"]}}})
          else:
            help = pract[loop]["date"]
            timeTemp = datetime.datetime.strptime(help, "%d %b %Y")
            if timeTemp < oneWeek:
              userData.update({"id": ctx.author.id}, {"$pull": {"practiceLog": {"date": pract[loop]["date"], "minutes": pract[loop]["minutes"]}}})
        except:
          pass
      try:
        userData.update_one({"id":ctx.author.id}, {"$update":{"practiceLog": {"date": timeNow,"minutes": str(amountPracticed)}}})
      except:
        userData.update_one({"id":ctx.author.id}, {"$push":{"practiceLog": {"date": timeNow,"minutes": str(amountPracticed)}}})
      
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
      getUserData(ctx.author.id) #Makes sure user in database
      goalMatch = userData.find_one({"id": ctx.author.id, "to-do": goal})
      if goalMatch is None:
        userData.update_one({"id": ctx.author.id}, {"$push": {"to-do": goal}})
        await ctx.send("Added goal "+goal)
        goal += " gs" #Goal set.
        #userData.update_one({"id":ctx.author.id}, {"$push":{"practiceLog": {timeNow: goal}}})
      else:
        await ctx.send("Goal already exists lah!")


  @commands.command(aliases = ["repertoire"], brief = "Displays active goals.", description = "Displays active goals.")
  async def goals(self, ctx):
    user = getUserData(ctx.author.id)
    items = user["to-do"]
    em = discord.Embed(title = f"{ctx.author.display_name}'s Goals", color = 15417396)
    em.set_thumbnail(url=ctx.author.avatar_url)
    for item in items:
      if item.find(",") == -1:
        em.add_field(name = item, value = "[no desc]", inline=False) #Ugly af I know but can't think of anything else
      else:
        x = item.split(",", 1)
        em.add_field(name = x[0], value = x[1], inline=False)
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

  @commands.command(aliases = ["fg"], brief = "Displays finished goals.", description = "Displays finished goals.")
  async def finishedgoals(self, ctx):
    user = getUserData(ctx.author.id)
    items = user["to-done"]
    em = discord.Embed(title = f"{ctx.author.display_name}'s Finished Goals", color = 15417396)
    em.set_thumbnail(url=ctx.author.avatar_url)
    for item in items:
      if item.find(",") == -1:
        em.add_field(name = item, value = "[no desc added]")
      else:
        x = item.split(",", 1)
        em.add_field(name = x[0], value = x[1])
    em.set_footer(text="Go practice lah!")
    await ctx.send(embed = em)
  
  @commands.command(aliases = ["statistics", "stat"], brief = "Shows user's stats.", description = "Shows user's stats, among other things.")
  async def stats(self, ctx,*,user:discord.Member = None):
    if user is None:
      user = ctx.author
    users = getUserData(user.id)
    bal = users["bubbleTea"]
    practice = str(users["practiceTime"])
    teams = users["team"]
    em = discord.Embed(title = f"{user.nick}'s stats", color = 15417396, description = f'''
    =====================
    Bubble tea: {bal}
    Practice Time: {practice} minutes
    =====================
    Team: {teams}''')
    em.set_thumbnail(url=user.avatar_url)
    em.set_footer(text="⏰ Go practice lah!")
    await ctx.send(embed = em)
  '''
  @commands.command(aliases = ["mgoal, minutes", "mg", "minutes"], brief = "Set a goal for amount of practice minutes.", description = "Set a goal for amount of practice minutes.")
  async def minutegoal(self, ctx, minutes):
    pass
  '''
  
  @commands.command(aliases = ["scales"], brief = "Generates a random scale.", description = "Generates a random scale, with arguments either 'dia' (diatonic), 'all' and 'maj', 'min', 'hmin', and 'mmin' (not added). You can also just type in any scale you want, with # for sharp and b for flat.")
  async def scale(self, ctx, *args):
    diamaj = ["cmaj.PNG","dmaj.PNG","emaj.PNG","fmaj.PNG","gmaj.PNG","amaj.PNG","bmaj.PNG"]
    diamin = ["cmin.PNG","dmin.PNG","emin.PNG","fmin.PNG","gmin.PNG","amin.PNG","bmin.PNG"]
    diahmin = ["chmin.PNG","dhmin.PNG","ehmin.PNG","fhmin.PNG","ghmin.PNG","ahmin.PNG","bhmin.PNG"]
    req = ""
    for x in args:
        req += x
        req += " "
    req= req[:-1].lower()
    if "diamaj" == req:
      choice = random.choice(diamaj)
      bud = choice[:-7].capitalize() + " Major"
    elif "diamin" == req:
      choice = random.choice(diamin)
      bud = choice[:-7].capitalize() + " Minor"
    elif "diahmin" == req:
      choice = random.choice(diahmin)
      bud = choice[:-8].capitalize() + " Harmonic Minor"
    else:
      choice = req+".PNG"
      try:
        if "hmin" in req:
          bud = req[:-4].capitalize() + " Harmonic Minor"
        elif "min" in req:
          bud = req[:-3].capitalize() + " Minor"
        elif "maj" in req:
          bud = req[:-3].capitalize() + " Major"
      except:
        await ctx.send("Something went wrong. Make sure you're typing things in the right format lah!")
        return
    try:
      file = discord.File(f"cogs/media/scales/{choice}")
      em = discord.Embed(title=bud, color = 15417396)
      em.set_image(url="attachment://image.png")
      await ctx.send(file=file, embed=em)
    except:
      await ctx.send("Something went wrong. Make sure you're typing things in the right format lah!")

  @commands.command(brief = "Set your instruments for all to see.", description = "Set your instruments for all to see. It includes every flair in r/lingling40hrs, and a few more. To see the full list, type 'p.instrument list *<section>'")
  async def instrument(self, ctx, *args):
    req = ""
    for x in args:
        req += x
        req += " "
    req= req[:-1].lower()
    strings = ["violin", "viola", "cello", "bass","guitar","harp","other string instrument"]
    woodwinds = ["oboe", "flute", "recorder", "clarinet", "bassoon", "saxophone", "other woodwind instrument"]
    brass = ["euphonium", "french horn", "trumpet", "trombone", "tuba", "other brass instrument"]
    keyboards = ["accordion", "piano", "other keyboard instrument"]
    other = ["percussion", "voice", "ethnic instrument", "composer", "audience"]
    newAll = strings + woodwinds + brass + keyboards + other
    if req == "":
      await ctx.send("You need to specify an instrument to set.")
    elif req in newAll:
      pass
      user = getUserData(ctx.author.id)
      items = user["instruments"]
      if req in items:
        await ctx.send("You already play this instrument.")
      elif len(items) >= 3:
        await ctx.send("You've already specified three instruments.")
      else:
        userData.update_one({"id":ctx.author.id}, {"$push":{"instruments": req}})
        await ctx.send("Instrument added.")
    elif "list" in req:
      meep = "- "
      if "string" in req:
        for i in strings:
          meep += i+"\n - "
      elif "wind" in req:
        for i in woodwinds:
          meep += i +"\n - "
      elif "brass" in req:
        for i in brass:
          meep += i + "\n - "
      elif "keyboards" in req:
        for i in keyboards:
          meep += i + "\n - "
      elif "other" in req:
        for i in other:
          meep += i + "\n - "
      else:
        for i in newAll:
          meep += i + "\n - "
      meep = meep[:-2]  
      em = discord.Embed(title = f"Instruments", color = 15417396, description = meep)
      await ctx.send(embed=em)
    else:
      await ctx.send("Invalid argument.")
      
def getUserData(x):
  userTeam = userData.find_one({"id": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "to-do": [], "to-done": [],"practiceLog": [], "practiceGoal": 0, "sprintRemaining": -10, "dailyLastCollected": d, "streak": 0,  "awards": [], "instrument": [], "clef": 0}
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