import discord
import dns
import os
import pymongo
from discord.ext import commands
import math
import datetime
cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]


class Teams(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases = ["t"], brief = "Join or leave a team.", description = "Join or leave a team.")
  @commands.cooldown(1, 172800, commands.BucketType.user)
  async def team(self, ctx, joinLeave = None, *args):
    if joinLeave == None:
      #Don't delete (Python doesn't handle string operations with Nonetype)
      await ctx.send("You need to specify whether you want to leave or join a team.")
      reset = 1
    elif joinLeave.lower() == "join":
      #Checks that team exists and isn't full.
      user = getUserData(ctx.author.id)
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
        userData.update_one({"id": ctx.author.id}, {"$set":{"team": teamJoin}})
        await ctx.send(f"Joined team {teamJoin} successfully.")
        reset = 0
    elif joinLeave.lower() == "leave":
      #Checks user is part of a team.
      user = getUserData(ctx.author.id)
      team = user["team"]
      if team == "None":
        await ctx.send("You're not a part of a team")
        reset = 1
      else:
        await ctx.send(f"Left {team} successfully.")
        userData.update_one({"id":ctx.author.id}, {"$set":{"team":"None"}})
        reset = 0
    else:
      await ctx.send("You need to specify whether you want to leave or join a team.")
      reset = 1
    
    #If the user makes a mistake in this command, cooldown resets.
    if reset == 1:
      ctx.command.reset_cooldown(ctx)

  @team.error
  async def team_error(self, ctx, error):
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
          userData.update_one({"id":ctx.author.id}, {"$set":{"team":teamJoin}})
          await ctx.send(f"Successfully created team {teamJoin}.")
        else:
          await ctx.send("That team name is already taken, please try again.")

      
#Helper function uwu
def getUserData(x):
  userTeam = userData.find_one({"id": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "streak": 0, "to-do": [], "practiceLog": [],"sprintRemaining": -10, "dailyLastCollected": d,"practiceGoal": 0}
    userData.insert_one(newUser)
  userTeam = userData.find_one({"id": x})
  return userTeam 
  


def setup(bot):
  bot.add_cog(Teams(bot))