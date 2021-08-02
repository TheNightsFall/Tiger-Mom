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
import json

cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]
teamData = cluster["tigermom"]["teams"]

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
    aP = int(amountPracticed)
    user = getUserData(ctx.author.id)
    minutes = user["practiceTime"]
    pract = user["practiceLog"]
    utcNow = pytz.utc.localize(datetime.datetime.utcnow())
    oneWeek = datetime.datetime.utcnow() - timedelta(days=31)
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
    if user["team"] != "None":
      team = getTeamData(user["team"])
      if team["qname"] != "None":
        tempor = team["qprog"][0]["pcont"]
        if str(ctx.author.id) in tempor:
          pass
        else:
          tempor += str(ctx.author.id)
          tempor += "|"
        aP = int(team["qprog"][0]["pday"])+aP
        #I gave up.
        teamData.update_one({"tn":team["tn"]}, {"$push": {"qprog": {"days":team["qprog"][0]["days"], "pday": aP, "pdone": team["qprog"][0]["pdone"],"pcont": tempor, "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
        teamData.update_one({"tn": team["tn"]}, {"$pull": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["pcont"], "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
        reee= checkQuest(team["tn"])
        if reee is None:
          pass
        else:
          await ctx.send(f"*'{reee[0]}'*\nHuzzah! Your team has finished a quest by PRACTICING! Ling Ling would be proud. Each member of your team is rewarded with {reee[1]} <:bubbletea:818865910034071572>. ")
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
    instr = users["instruments"]
    help = ""
    for x in instr:
      help += x
      help += ", "
    instr = help[:-2]
    teams = users["team"]
    line1 = ""
    for x in range(1,len(user.name)+10):
      line1 += "─"
    em = discord.Embed(title = f"{user.name}`#{ctx.author.discriminator}`", color = 15417396, description = f'''
    {line1}
    :violin: | {instr}\n
    ⏰ | {practice} minutes\n
    <:bubbletea:818865910034071572> | {bal}
    {line1}
    Team | {teams}''')
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
    diamaj = []
    diamin = ["cmin.PNG","dmin.PNG","emin.PNG","fmin.PNG","gmin.PNG","amin.PNG","bmin.PNG"]
    diahmin = ["chmin.PNG","dhmin.PNG","ehmin.PNG","fhmin.PNG","ghmin.PNG","ahmin.PNG","bhmin.PNG"]
    diammin = ["cmmin.PNG","dmmin.PNG","emmin.PNG","fmmin.PNG","gmmin.PNG","ammin.PNG","bmmin.PNG"]
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
    elif "diammin" == req:
      choice = random.choice(diammin)
      bud = choice[:-8].capitalize() + " Melodic Minor"
    elif "allmaj" == req:
      pass
    else:
      choice = req+".PNG"
      try:
        if "hmin" in req:
          bud = req[:-4].capitalize() + " Harmonic Minor"
        elif "mmin" in req:
          bud = req[:-4].capitalize() + " Melodic Minor"
        elif "min" in req:
          bud = req[:-3].capitalize() + " Minor"
        elif "maj" in req:
          bud = req[:-3].capitalize() + " Major"
        else:
          await ctx.send("Check your formatting lah!")
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
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "to-do": [], "to-done": [],"practiceLog": [], "practiceGoal": 0, "sprintRemaining": -10, "dailyLastCollected": d, "streak": 0, "instrument": [], "clef": 0}
    userData.insert_one(newUser)
  userTeam = userData.find_one({"id": x})
  return userTeam

def getTeamData(x):
  userTeam = teamData.find_one({"tn": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newTeam = {"tn": x, "xp": 0, "qname": "None", "qreq": [], "qprog": [], "gamed": d, "members": [], "captains": [], "bans": [], "pending": [], "challenges": [], "accepted": [],"stats": []}
    teamData.insert_one(newTeam)
  userTeam = teamData.find_one({"tn": x})
  return userTeam
  
def checkQuest(y):
  x=getTeamData(y)
  diff = x["qname"][:1]
  if diff == "E":
    diff = 10
  elif diff == "M":
    diff = 30
  else:
    diff = 60
  utcNow = pytz.utc.localize(datetime.datetime.utcnow())
  timeNow = utcNow.strftime("%d %b %Y")
  daysOld = x["qprog"][0]["days"]
  tGames = x["qprog"][0]["tg"]
  contributors = x["qprog"][0]["pcont"]
  contributor = contributors.count("|")
  if x["qprog"][0]["pday"] >= diff and x["qprog"][0]["pdone"] != timeNow:
    daysOld = daysOld+ 1 if x["qprog"][0]["days"] < x["qreq"][0]["days"] else x["qreq"][0]["days"]
  elif x["qprog"][0]["pday"] >= diff and x["qprog"][0]["pdone"] == timeNow:
    pass
  else:
    timeNow = x["qprog"][0]["pdone"]
  if x["qreq"][0]["days"] == daysOld:
    if contributor >= x["qreq"][0]["pN"]:
      if tGames >= x["qreq"][0]["tg"]:
        tGames = x["qreq"][0]["tg"]
        if x["qprog"][0]["bb"] >= x["qreq"][0]["bb"]:
          members = list(x["members"])
          with open('cogs/media/quests.json') as f:
            data = json.load(f)
          f.close()
          title = x["qname"][1:]
          amount = data[title]["Reward"]
          for member in members:
            temp1 = getUserData(member)
            Bal = temp1["bubbleTea"]
            Bal += amount
            userData.update_one({"id": member}, {"$set": {"bubbleTea": Bal}})
          teamData.update_one({"tn": x["tn"]}, {"$pull": {"qprog": {"days":x["qprog"][0]["days"], "pday": x["qprog"][0]["pday"], "pdone": x["qprog"][0]["pdone"],"pcont": x["qprog"][0]["pcont"], "tg": x["qprog"][0]["tg"], "bb": x["qprog"][0]["tg"]}}})
          teamData.update_one({"tn": x["tn"]}, {"$pull": {"qreq": {"days": x["qreq"][0]["days"], "pN": x["qreq"][0]["pN"], "tg": x["qreq"][0]["tg"], "bb": x["qreq"][0]["bb"]}}})
          teamData.update_one({"tn":x["tn"]}, {"$set": {"qname": "None"}})
          return [data[title]["FinishText"],amount]
  teamData.update_one({"tn": x["tn"]}, {"$push": {"qprog": {"days":daysOld, "pday": x["qprog"][0]["pday"], "pdone": timeNow,"pcont": contributors, "tg": tGames, "bb": x["qprog"][0]["bb"]}}})
  teamData.update_one({"tn": x["tn"]}, {"$pull": {"qprog": {"days":x["qprog"][0]["days"], "pday": x["qprog"][0]["pday"], "pdone": x["qprog"][0]["pdone"],"pcont": x["qprog"][0]["pcont"], "tg": x["qprog"][0]["tg"], "bb": x["qprog"][0]["bb"]}}})
  return
          
    #Check contributing members, tg, bb
def setup(bot):
  bot.add_cog(Practice(bot))
