import discord
import dns
import os
import pymongo
from discord.ext import commands
import asyncio
import math
import random
import datetime
cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]
teamData = cluster["tigermom"]["teams"]


class Teams(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases = ["j"], brief = "Join a team.", description = "Join a team.")
  @commands.cooldown(1, 172800, commands.BucketType.user)
  async def join(self, ctx, *args):
    user = getUserData(ctx.author.id)
    team = user["team"]
    if team == "None":
      memberCount = 0
      teamJoin = ""
      for x in args:
        teamJoin += x
        teamJoin += " "
      teamJoin = teamJoin[:-1]
      for x in userData.find({"team": teamJoin}):
        memberCount += 1
      if memberCount == 0:
        await ctx.send("Team doesn't exist. Use 'p.create' to make a team.")
        reset = 1
      elif memberCount >= 10:
        await ctx.send("Team is full.")
        reset = 1
      else:
        teamBan = teamData.find_one({"tn": teamJoin})
        ban = teamBan["bans"]
        boing = []
        for x in ban:
          if str(x) == str(ctx.author.id):
            boing.append(x)
        if boing == []:
          getTeamData(teamJoin)
          userData.update_one({"id": ctx.author.id}, {"$set":{"team": teamJoin}})
          teamData.update_one({"tn": teamJoin}, {"$push" :{"members": ctx.author.id}})
          await ctx.send(f"Joined team {teamJoin} successfully.")
          reset = 0
        else:
          await ctx.send("You are banned from this team.")
          reset = 1
    else:
      reset = 1
      await ctx.send("You're already part of a team lah!")
    if reset == 1:
      ctx.command.reset_cooldown(ctx)
  @join.error
  async def joinError(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      seconds = math.floor(error.retry_after)
      if seconds > 3600:
        hours = str(math.floor(seconds/3600))
        minutes = str(math.floor((int(seconds) - int(hours)*3600)/60))
        await ctx.send("You count time as bad as you practice, no wonder you not doctor. Try again in "+hours+" hours and "+minutes+" minutes.")
      elif seconds < 60:
        await ctx.send("You count time as bad as you practice, no wonder you not doctor. Try again in "+seconds+" seconds.")
      else:
        minutes = str(math.floor(seconds/60))
        await ctx.send("You count time as bad as you practice, no wonder you not doctor. Try again in " + minutes + " minutes.")
    else:
      raise error
  #Still need to check if user is the last captain
  @commands.command(brief = "Leave a team.", description = "Leave a team.")
  async def leave(self, ctx):
    #Checks user is part of a team.
    user = getUserData(ctx.author.id)
    team = user["team"]
    if team == "None":
      await ctx.send("You're not a part of a team")
      reset = 1
    else:
      temp = getTeamData(team)
      mem = temp["members"]
      if len(mem) == 1:
        teamData.delete_one({"members": mem})
      else:
        teamData.update({"tn": team}, {"$pull" :{"members": ctx.author.id}})
        try:
          teamData.update({"tn": team}, {"$pull" :{"captains": ctx.author.id}})
        except:
          pass
      userData.update_one({"id":ctx.author.id}, {"$set":{"team":"None"}})
      await ctx.send(f"Left {team} successfully.")
      reset = 0
    #If the user makes a mistake in this command, cooldown resets.
    if reset == 1:
      ctx.command.reset_cooldown(ctx)
  @leave.error
  async def leaveError(self, ctx, error):
    #Ling ling already doctor lah!
    if isinstance(error, commands.CommandOnCooldown):
      seconds = math.floor(error.retry_after)
      if seconds > 3600:
        hours = str(math.floor(seconds/3600))
        minutes = str(math.floor((int(seconds) - int(hours)*3600)/60))
        await ctx.send("You count time as bad as you practice, no wonder you not doctor. Try again in "+hours+" hours and "+minutes+" minutes.")
      elif seconds < 60:
        await ctx.send("You count time as bad as you practice, no wonder you not doctor. Try again in "+seconds+" seconds.")
      else:
        minutes = str(math.floor(seconds/60))
        await ctx.send("You count time as bad as you practice, no wonder you not doctor. Try again in " + minutes + " minutes.")
    else:
      raise error
  @commands.command(brief = "Create a team.", description = "Create a team.")
  async def create(self, ctx, *args):
    teamJoin = ""
    for x in args:
        teamJoin += x
        teamJoin += " "
    teamJoin = teamJoin[:-1]
    
    if teamJoin is None:
      await ctx.send("You can't create a team without a name.")
    else:
      user = getUserData(ctx.author.id)
      team = user["team"]
      if team != "None":
        await ctx.send("You can't create a team when you're already part of one!")
      else:
        teamNameTaken = userData.find_one({"team": teamJoin})
        if teamNameTaken is None:
          user = getTeamData(teamJoin)
          userData.update_one({"id":ctx.author.id}, {"$set":{"team":teamJoin}})
          teamData.update_one({"tn": teamJoin}, {"$push" :{"members": ctx.author.id}})
          teamData.update_one({"tn": teamJoin}, {"$push" :{"captains": ctx.author.id}})
          await ctx.send(f"Successfully created team {teamJoin}.")
        else:
          await ctx.send("That team name is already taken, please try again.")
  #Update this more later
  @commands.command(aliases = ["th", "thelp", "teamh"], brief = "Overview of teams.", description = "An overview of teams.")
  async def teamhelp(self, ctx):
    hContent = '''
    ===================================
    **The Basics:**
    ===================================
    Each team can have up to 10 members, 
    and technically up to 10 captains 
    as well. All members can view the
    team's inbox, put/vote in ban 
    appeals, and accept challenges, but 
    captains can change the team name,
    icon, send challenges, and have more
    weight in ban appeals.

    '''
    em = discord.Embed(title = "An overview of teams...", color = 15417396, description = hContent)
    await ctx.send(embed = em)
  
  @commands.command(brief = "Put in a ban appeal.", description = "Put in a ban appeal.")
  @commands.cooldown(1, 345600, commands.BucketType.user)
  async def ban(self, ctx, user:discord.Member = None):
      if user == None:
        await ctx.send("You need to specify a member lah!")
        ctx.command.reset_cooldown(ctx)
        return
      banApp = user.id
      temp = getUserData(ctx.author.id)
      team = temp["team"]
      if team == "None":
        await ctx.send("You're not part of a team lah!")
        ctx.command.reset_cooldown(ctx)
        return
      banListTemp = getTeamData(team)
      captains = banListTemp["captains"]
      bannerIsCap = 0
      banneeIsCap = 0
      for captain in captains:
        if str(captain) == str(ctx.author.id):
          bannerIsCap = 1
        if str(captain) == str(banApp):
          banneeIsCap = 1
      if bannerIsCap == 1 and banneeIsCap == 0:
        banList = banListTemp["pending"]
        for x in banList:
          if str(user.id) in x:
            teamData.update_one({"tn": team}, {"$pull" :{"pending": x}})
        teamData.update_one({"tn": team}, {"$push" :{"bans": banApp}})
        teamData.update_one({"tn": team}, {"$pull" :{"members": banApp}})
        userData.update_one({"id": banApp}, {"$set":{"team": "None"}})
        await ctx.send(f"{user.mention} was banned from team {team}.")
        return
      else:
        banList = banListTemp["pending"]
        for x in banList:
          if str(user.id) in x:
            print(x)
            #Maybe give captains more weight, who knows.
            currentNum = x[-1]+2 if bannerIsCap == 1 else x[-1]+1
            y = str(user.id)+": "+str(currentNum)
            threshold = 5 if banneeIsCap == 0 else 7
            if y < threshold:
              teamData.update_many({"pending": x}, {"$set": {"pending.$": y}})
              await ctx.send("Your vote has been recorded.")
              return
            else:
              teamData.update_one({"tn": team}, {"$pull" :{"pending": x}})
              teamData.update_one({"tn": team}, {"$pull" :{"members": banApp}})
              userData.update_one({"id": banApp}, {"$set":{"team": "None"}})
              if banneeIsCap == 1:
                teamData.update_one({"tn": team}, {"$pull" :{"captains": banApp}})
              await ctx.send("Your vote has been recorded, this user has been banned.")
              return
        x = str(banApp)+": 2" if bannerIsCap == 1 else str(banApp)+": 1"
        teamData.update_one({"tn": team}, {"$push": {"pending": x}})
        await ctx.send("Your vote has been recorded.")
      
  @commands.command(brief = "Play a team game.", description = "Play a team game.")
  async def game(self, ctx):
    pieces = ["https://imgur.com/ap3xhAx.png","https://imgur.com/YlXwca6.png","https://imgur.com/bAzulbm.png","https://imgur.com/rTy01R7.png","https://imgur.com/XK1N3v6.png","https://imgur.com/Uq77WqN.png","https://imgur.com/QlRRgZa.png","https://imgur.com/kEw5Xy5.png"]
    era = ['5️⃣', '4️⃣', '3️⃣', '4️⃣', '2️⃣', '5️⃣', '4️⃣', '4️⃣']
    composer = ["rachmaninoff", "schubert", "mozart", "bizet", "bach", "stravinsky", "smetana", "bazzini"]
    piece = random.randint(0,7)
    print(piece)
    temp = getUserData(ctx.author.id)
    tem = temp["team"]
    temp = getTeamData(tem)
    validMembers = temp["members"]
    print(validMembers)
    points = 0
    em = discord.Embed(title = "Question 1 - Guess the era of the piece shown.", description = "Reactions from left to right, renaissance, baroque, classical, romantic, 20th century, contemporary.",color = 15417396)
    em.set_image(url=pieces[piece])
    em.set_footer(text=f"You have 6 minutes to finish the game as a team {tem}.")
    msg = await ctx.send(embed=em)
    await msg.add_reaction('1️⃣')
    await msg.add_reaction('2️⃣')
    await msg.add_reaction('3️⃣')
    await msg.add_reaction('4️⃣')
    await msg.add_reaction('5️⃣')
    await msg.add_reaction('6️⃣')
    try:
      answer = await self.bot.wait_for('reaction_add', check= lambda reaction, user: user.id in validMembers, timeout=600)
      print(answer[0], era[piece])
      if str(answer[0]) == str(era[piece]):
        points += 1
      em = discord.Embed(title = "Question 2 - Guess the composer of the piece, by last name.", description = "Send it in a message.", color = 15417396)
      em.set_image(url=pieces[piece])
      em.set_footer(text=f"You have 6 minutes to finish the game as a team {tem}.")
      await ctx.send(embed=em)
      Answer = str(await self.bot.wait_for('message', check = lambda message: message.id in validMembers))
      print(Answer)
      if str(Answer.lower()) == str(composer[piece]):
        points += 3
        print("corrrrrect")
      em = discord.Embed(title = "Question 3 - What type of piece was it originally?", description = "Valid answers include solo, concerto, symphony, concert band, jazz band, string orchestra, duet, trio, quartet, quintet.")
      em.set_image(url=pieces[piece])
      em.set_footer(text=f"You have 6 minutes to finish the game as a team {tem}.")
    except asyncio.TimeoutError:
      await ctx.send(f"You too slow lah! Game over with {points} points.")

#Helper function uwu
def getUserData(x):
  userTeam = userData.find_one({"id": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "streak": 0, "to-do": [], "practiceLog": [],"sprintRemaining": -10, "dailyLastCollected": d,"practiceGoal": 0, "to-done": [], "awards": []}
    userData.insert_one(newUser)
  userTeam = userData.find_one({"id": x})
  return userTeam 
  
def getTeamData(x):
  userTeam = teamData.find_one({"tn": x})
  if userTeam is None:
    newTeam = {"tn": x, "xp": 0, "questday": 0, "gamenum": 0, "members": [], "captains": [], "bans": [], "pending": [], "challenges": []}
    teamData.insert_one(newTeam)
  userTeam = teamData.find_one({"tn": x})
  return userTeam

def setup(bot):
  bot.add_cog(Teams(bot))