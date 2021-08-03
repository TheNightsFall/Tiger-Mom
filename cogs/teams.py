import discord
import dns
import os
import pymongo
from discord.ext import commands
#from discord import ActionRow, Button, ButtonColor
import asyncio
import math
import random
import datetime
from datetime import timedelta
import json
import pytz
import math
cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]
teamData = cluster["tigermom"]["teams"]
#Use for icons:https://thenounproject.com/microdotgraphic/collection/music-instrument/

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
      for x in userData.find({"team": teamJoin}): memberCount += 1
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
      cpt = temp["captains"]
      if len(mem) == 1:
        teamData.delete_one({"members": mem})
      else:
        if len(cpt) == 1:
          ctx.command.reset_cooldown(ctx)
          await ctx.send("You're the last captain! Please assign someone else as captain before you leave")
          return
        teamData.update({"tn": team}, {"$pull" :{"members": ctx.author.id}})
        try:
          teamData.update({"tn": team}, {"$pull" :{"captains": ctx.author.id}})
        except:
          pass
      userData.update_one({"id":ctx.author.id}, {"$set":{"team":"None"}})
      await ctx.send(f"Left {team} successfully.")
      reset = 0
    if reset == 1:
      ctx.command.reset_cooldown(ctx)
  @leave.error
  async def leaveError(self, ctx, error):
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
    elif teamJoin == "None":
      await ctx.send("Not a valid team name.")
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
  
  @commands.command(aliases = ["kick"], brief = "Put in a ban appeal.", description = "Put in a ban appeal.")
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
      bannerIsCap, banneeIsCap = 0
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
        await ctx.send(":ballot_box_with_checkmark: Your vote has been recorded.")

  @commands.command(aliases=["dm"], brief="Demote someone from captain.", description = "Demote someone from captain.")
  @commands.cooldown(1, 6000, commands.BucketType.user)
  async def demote(self, ctx, user:discord.Member = None):
    if user is None:
      await ctx.send("You must pick someone to demote from captain lah!")
      ctx.command.reset_cooldown(ctx)
      return
    temp = getUserData(ctx.author.id)
    team = temp["team"]
    if team == "None":
      await ctx.send("You're not part of a team lah!")
      ctx.command.reset_cooldown(ctx)
      return
    team = getTeamData(team)
    capts = team["captains"]
    if ctx.author.id == capts[0]:
      if user.id in capts:
        teamData.update_one({"tn": team["tn"]}, {"$pull": {"captains": user.id}})
        await ctx.send("User demoted.")
      else:
        await ctx.send("That user is not a captain of your team!")
    else:
      await ctx.send("You're not the team's founder/foremost captain, you do not have permission to do this.")
  @commands.command(aliases = ["capt", "cap", "promote"], brief="Promote someone to captain", description="Promote someone to captain")
  @commands.cooldown(1, 6000, commands.BucketType.user)
  async def captains(self, ctx, user:discord.Member = None):
    if user is None:
      await ctx.send("You must pick someone to promote to captain!")
      ctx.command.reset_cooldown(ctx)
      return
    temp = getUserData(ctx.author.id)
    team = temp["team"]
    if team == "None":
      await ctx.send("You're not part of a team lah!")
      ctx.command.reset_cooldown(ctx)
      return
    Temp = getTeamData(team)
    tn = Temp["tn"]
    captains = Temp["captains"]
    uIC = 0
    newCapt = self.bot.get_user(user.id)
    for captain in captains:
      if captain == user.id:
        await ctx.send("This person is already a captain.")
        ctx.command.reset_cooldown(ctx)
        return
      elif captain == ctx.author.id:
        uIC = 1
    if uIC == 1:
      teamData.update_one({"tn": tn}, {"$push" :{"captains": user.id}})
      await ctx.send(f"Promoted {newCapt} to captain.")
    else:
      await ctx.send(f"You don't have permission to promote {newCapt} to captain")
      ctx.command.reset_cooldown(ctx)
      return
  
  @commands.command(aliases = ["display", "dis", "t"], brief = "Displays your team and its members.", description = "Displays your team and its members.")
  @commands.cooldown(1, 30, commands.BucketType.user)
  async def team(self, ctx, *args):
    team = ""
    for x in args:
        team += x
        team += " "
    if team == "":
      temp = getUserData(ctx.author.id)
      team = temp["team"]
      if team == "None":
        await ctx.send("You're not part of a team!")
        ctx.command.reset_cooldown(ctx)
        return
    else:
      team = team[:-1]
    team = teamData.find_one({"tn": team})
    if team is None:
      await ctx.send("Team doesn't exist. Make sure to capitalize and spell correctly!")
      ctx.command.reset_cooldown(ctx)
      return
    names = team["members"]
    xp = team["xp"]
    desc = f'''xp: {xp} chal:
    ―――――――――――――――――――――――――
    '''
    em = discord.Embed(title = team["tn"], color = 15417396, description = desc)
      
    em.set_footer(text ="Go practice lah! ⏰", icon_url = ctx.author.avatar_url)
    loop = 0
    for name in names:
      loop += 1
      user = getUserData(name)
      bal = user["bubbleTea"]
      displayName = str(self.bot.get_user(int(name)))
      name = str(loop)+". "+displayName[:-5]
      em.add_field(name=name, value = f"Bal: {bal}", inline=False)
    await ctx.send(embed=em)
  
  @team.error
  async def team_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(f"Wait {round(error.retry_after,3)} seconds. I sichuan your pepper!!")
    else:
      raise error
  
  @commands.command(aliases = ["chal"], brief = "Challenge a team.", description = "Challenge a team.")
  @commands.cooldown(1, 3600, commands.BucketType.user)
  async def challenge(self, ctx, *args):
    temp = getUserData(ctx.author.id)
    team1 = temp["team"]
    if team1 == "None":
      await ctx.send("You're not part of a team!")
      return
    team = getTeamData(team1)
    teamChal = ""
    for x in args:
        teamChal += x
        teamChal += " "
    teamChal = teamChal[:-1]
    if teamChal == team["tn"]:
      await ctx.send("You can't challenge your own team!")
      ctx.command.reset_cooldown(ctx)
      return
    elif teamChal == "":
      await ctx.send("You must specify a team to challenge!")
      ctx.command.reset_cooldown(ctx)
      return
    if team["accepted"] != []:
      await ctx.send("You cannot send challenges while in one.")
      return
    for x in teamData.find({"tn": teamChal}):
      utcNow = pytz.utc.localize(datetime.datetime.utcnow())
      expiration = utcNow + timedelta(days=1)
      expiration = expiration.strftime("%m/%d/%Y %H:%M:%S")	
      teamData.update_one({"tn": team1}, {"$push" :{"challenges": {"o": {"expiration": expiration, "challenged": teamChal}}}})
      teamData.update_one({"tn": teamChal}, {"$push" :{"challenges": {"i": {"expiration": expiration, "challenged": team1}}}})
      await ctx.send(f"Challenge sent to {teamChal}.")
      return
    await ctx.send(f"Team {teamChal} does not exist.")

  @commands.command(aliases = ["accepted", "acc"], brief = "Accept a challenge from another team.", desription = "Accept a challenge from another team.")
  @commands.cooldown(1, 86400, commands.BucketType.user) #86400
  async def accept(self, ctx, *args):
    teamChal = ""
    for x in args:
        teamChal += x
        teamChal += " "
    teamChal = teamChal[:-1]
    if teamChal == "":
      await ctx.send("You must specify a team's challenge to accept lah!")
      ctx.command.reset_cooldown(ctx)
      return
    temp = getUserData(ctx.author.id)
    team = temp["team"]
    if team == "None":
      await ctx.send("You're not part of a team!")
      return
    team = getTeamData(team)
    if teamChal == team["tn"]:
      await ctx.send("You can't challenge your own team lah!")
      ctx.command.reset_cooldown(ctx)
      return
    if team["accepted"] == []:
      pass
    else:
      await ctx.send("Your team is in the middle of a challenge. You currently cannot send nor accept any additional challenges.")
      return
    chal = team["challenges"]
    outCap =team["captains"]
    tn = team["tn"]
    inb = []
    out = []
    for mail in chal:
      if str(mail)[2] == "i":
        inb.append(mail)
      else:
        out.append(mail)
    
    try:
      userTeam = teamData.find_one({"tn": teamChal})
      if userTeam["accepted"] == []:
        pass
      else:
        await ctx.send(f"Team {teamChal} is already participating in a challenge.")
        return
    except:
      await ctx.send("Team does not exist lah! Check your spelling and capitalization!")
      return
    current = datetime.datetime.now()
    inCap = userTeam["captains"]
    loop = -1
    for x in inb:
      loop += 1
      timeChal = datetime.datetime.strptime(inb[loop]["i"]["expiration"], "%m/%d/%Y %H:%M:%S")
      if inb[loop]["i"]["challenged"] == teamChal:
        teamData.update({"tn": team["tn"]}, {"$pull": {"challenges": {"i": {"expiration": inb[loop]["i"]["expiration"], "challenged": inb[loop]["i"]["challenged"]}}}})
        teamData.update({"tn": inb[loop]["i"]["challenged"]}, {"$pull": {"challenges": {"o": {"expiration": inb[loop]["i"]["expiration"], "challenged": team["tn"]}}}})
        del inb[loop]
        if current <= timeChal:
          utcNow = pytz.utc.localize(datetime.datetime.utcnow())
          expiration = utcNow + timedelta(days=1)
          expiration = expiration.strftime("%m/%d/%Y %H:%M:%S")	
          teamData.update({"tn": team["tn"]}, {"$push": {"accepted": {"expiration": expiration, "challenged": teamChal, "bal": 0}}})
          teamData.update({"tn": teamChal}, {"$push": {"accepted": {"expiration": expiration, "challenged": team["tn"], "bal": 0}}})
          emO = discord.Embed(title = "ATTENTION! CHALLENGE STARTED!", description = f"Hello, captains of {teamChal}! Team {tn} has accepted your challenge. For the next 24 hours, you will be competing against them to gather the most bubble tea. You will also be unable to accept or send out any other challenges.", color =	4373885)
          emO.timestamp = datetime.datetime.utcnow()
          emI = discord.Embed(title = "ATTENTION! CHALLENGE STARTED!", description = f"Hello, captains of {tn}! Captain {ctx.author} has accepted a challenge from {teamChal}! For the next 24 hours, you will be competing against them to gather the most bubble tea. You will also be unable to accept or send out any other challenges.", color = 4373885)
          emI.timestamp = datetime.datetime.utcnow()
          for captain in outCap:
            check = self.bot.get_user(int(captain))
            channel = await check.create_dm()
            await channel.send(embed = emI)
          for captain in inCap:
            check = self.bot.get_user(int(captain))
            channel = await check.create_dm()
            await channel.send(embed = emO)
          loop2 = -1
          for x in inb:
            loop2 += 1
            timeChal = datetime.datetime.strptime(inb[loop2]["i"]["expiration"], "%m/%d/%Y %H:%M:%S")
            timeNew = timeChal + timedelta(days=1)
            expiration = timeNew.strftime("%m/%d/%Y %H:%M:%S")
            teamData.update_one({"tn": team["tn"]}, {"$pull": {"challenges": {"i": {"expiration": inb[loop2]["i"]["expiration"], "challenged": inb[loop2]["i"]["challenged"]}}}})
            teamData.update_one({"tn": inb[loop2]["i"]["challenged"]}, {"$pull": {"challenges": {"o": {"expiration": inb[loop2]["i"]["expiration"], "challenged": team["tn"]}}}})
            teamData.update_one({"tn": team["tn"]}, {"$push": {"challenges": {"i": {"expiration": expiration, "challenged": inb[loop2]["i"]["challenged"]}}}})
            teamData.update_one({"tn": inb[loop2]["i"]["challenged"]}, {"$push": {"challenges": {"o": {"expiration": expiration, "challenged": team["tn"]}}}})
          loop3 = -1 #kill me now
          for x in out:
            loop3 += 1
            timeChal = datetime.datetime.strptime(out[loop3]["o"]["expiration"], "%m/%d/%Y %H:%M:%S")
            timeNew = timeChal + timedelta(days=1)
            expiration = timeNew.strftime("%m/%d/%Y %H:%M:%S")
            teamData.update({"tn": team["tn"]}, {"$pull": {"challenges": {"o": {"expiration": out[loop3]["o"]["expiration"], "challenged": out[loop3]["o"]["challenged"]}}}})
            teamData.update({"tn": out[loop3]["o"]["challenged"]}, {"$pull": {"challenges": {"i": {"expiration": out[loop3]["o"]["expiration"], "challenged": team["tn"]}}}})
            teamData.update({"tn": team["tn"]}, {"$push": {"challenges": {"o": {"expiration": expiration, "challenged": out[loop3]["o"]["challenged"]}}}})
            teamData.update({"tn": out[loop3]["o"]["challenged"]}, {"$push": {"challenges": {"i": {"expiration": expiration, "challenged": team["tn"]}}}})
          return
    await ctx.send("You don't have any incoming challenges lah!")
        
        
  @commands.command(aliases = ["dec", "reject", "whyyougottabesorude"], brief = "Decline incoming challenges.", description = "Decline incoming challenges.")
  @commands.cooldown(1,60, commands.BucketType.user)
  async def decline(self, ctx, *args):
    teamChal = ""
    for x in args:
        teamChal += x
        teamChal += " "
    teamChal = teamChal[:-1]
    if teamChal == "":
      await ctx.send("You must specify a team's challenge to decline lah!")
      ctx.command.reset_cooldown(ctx)
      return
    temp = getUserData(ctx.author.id)
    team = temp["team"]
    if team == "None":
      await ctx.send("You're not part of a team!")
      return
    team = getTeamData(team)
    chal = team["challenges"]
    inb = []
    for mail in chal:
      if str(mail)[2] == "i":
        inb.append(mail)
    if inb == []:
      await ctx.send("Your team has no incoming challenges.")
      ctx.command.reset_cooldown(ctx)
      return
    current = datetime.datetime.now()
    loop = -1
    chalDec = 0
    for x in inb:
      loop += 1
      timeChal = datetime.datetime.strptime(inb[loop]["i"]["expiration"], "%m/%d/%Y %H:%M:%S")
      if current >= timeChal or inb[loop]["i"]["challenged"] == teamChal:
        teamData.update({"tn": team["tn"]}, {"$pull": {"challenges": {"i": {"expiration": inb[loop]["i"]["expiration"], "challenged": inb[loop]["i"]["challenged"]}}}})
        teamData.update({"tn": inb[loop]["i"]["challenged"]}, {"$pull": {"challenges": {"o": {"expiration": inb[loop]["i"]["expiration"], "challenged": team["tn"]}}}})
        chalDec += 1
    if chalDec == 0:
      await ctx.send(f"No incoming challenges from team {teamChal}.")
    else:
      await ctx.send(f"{chalDec} challenges declined.")

  @decline.error
  async def declineError(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      seconds = math.floor(error.retry_after)
      await ctx.send(f"Try again in {seconds} seconds lah!")

  @commands.command(aliases = ["recall"], brief = "Cancel outgoing challenges.", description = "Cancel outgoing challenges.")
  @commands.cooldown(1,60, commands.BucketType.user)
  async def cancel(self, ctx, *args):
    teamChal = ""
    for x in args:
        teamChal += x
        teamChal += " "
    teamChal = teamChal[:-1]
    if teamChal == "":
      await ctx.send("You must specify a challenge to cancel.")
      ctx.command.reset_cooldown(ctx)
      return
    temp = getUserData(ctx.author.id)
    team = temp["team"]
    if team == "None":
      await ctx.send("You're not part of a team!")
      return
    team = getTeamData(team)
    chal = team["challenges"]
    out = []
    for mail in chal:
      if str(mail)[2] == "o":
        out.append(mail)
    if out == []:
      await ctx.send("Your team has no outgoing challenges.")
      return
    current = datetime.datetime.now()
    loop = -1
    chalCan = 0
    for x in out:
      loop += 1
      timeChal = datetime.datetime.strptime(out[loop]["o"]["expiration"], "%m/%d/%Y %H:%M:%S")
      if current <= timeChal or out[loop]["o"]["challenged"] == teamChal:
        teamData.update({"tn": team["tn"]}, {"$pull": {"challenges": {"o": {"expiration": out[loop]["o"]["expiration"], "challenged": out[loop]["o"]["challenged"]}}}})
        teamData.update({"tn": out[loop]["o"]["challenged"]}, {"$pull": {"challenges": {"i": {"expiration": out[loop]["o"]["expiration"], "challenged": team["tn"]}}}})
        chalCan += 1
    if chalCan == 0:
      await ctx.send(f"No challenges sent to {teamChal}.")
    else:
      await ctx.send(f"{chalCan} challenges canceled.")
    
  @cancel.error
  async def cancelError(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      seconds = math.floor(error.retry_after)
      await ctx.send(f"Try again in {seconds} seconds lah!")

  @commands.command(aliases=["mail","messages"], brief = "View your ingoing and outgoing challenges.", description = "View your ingoing and outgoing challenges.")
  @commands.cooldown(1, 60, commands.BucketType.user)
  async def mailbox(self, ctx):
    liszt = ["▶️"]
    temp = getUserData(ctx.author.id)
    team = temp["team"]
    if team == "None":
      await ctx.send("You're not part of a team!")
      return
    team = getTeamData(team)
    inbox = team["challenges"]
    ingoing = []
    outgoing = []
    if inbox == []:
      emI = discord.Embed(title = "✉️ Inbox", description = "It's empty.", color =	4373885)
      await ctx.send(embed = emI)
      return
    else:
      for mail in inbox:
        if str(mail)[2] == "o":
          outgoing.append(mail)
        else:
          ingoing.append(mail)
      current = datetime.datetime.now()
      emO = discord.Embed(title = "✉️ Mail Outgoing", color = 15417396)
      emO.set_footer(text="⏰ Go practice lah!")
      emI = discord.Embed(title = "✉️ Inbox", color = 15417396)
      emI.set_footer(text="⏰ Go practice lah!")
      loop = -1
      #Makes the outgoing embed
      for x in outgoing:
        loop += 1
        timeChal = datetime.datetime.strptime(outgoing[loop]["o"]["expiration"], "%m/%d/%Y %H:%M:%S")
        if current >= timeChal:
          #Pulling stuff if it's expired from your team, then from other team
          teamData.update({"tn": team["tn"]}, {"$pull": {"challenges": {"o": {"expiration": outgoing[loop]["o"]["expiration"], "challenged": outgoing[loop]["o"]["challenged"]}}}})
          teamData.update({"tn": outgoing[loop]["o"]["challenged"]}, {"$pull": {"challenges": {"i": {"expiration": outgoing[loop]["o"]["expiration"], "challenged": team["tn"]}}}})
          loop -=1
        else:
          expiration = "Expires: "+outgoing[loop]["o"]["expiration"]
          emO.add_field(name=outgoing[loop]["o"]["challenged"], value = expiration, inline=False)
      if loop == -1:
        emO.add_field(name="Sorry, there's nothing outgoing.", value = "you can use p.chal <team name> to challenge another team.")
      loop = -1
      #Now to put stuff in ingoing.
      for x in ingoing:
        loop += 1
        timeChal = datetime.datetime.strptime(ingoing[loop]["i"]["expiration"], "%m/%d/%Y %H:%M:%S")
        if current >= timeChal:
          #Deleting things, yet to have tested if this works
          print(ingoing[loop]["i"]["challenged"])
          teamData.update({"tn": team["tn"]}, {"$pull": {"challenges": {"i": {"expiration": ingoing[loop]["i"]["expiration"], "challenged": ingoing[loop]["i"]["challenged"]}}}})
          teamData.update({"tn": ingoing[loop]["i"]["challenged"]}, {"$pull": {"challenges": {"o": {"expiration": ingoing[loop]["i"]["expiration"], "challenged": team["tn"]}}}})
          loop -=1
        else:
          expiration = "Expires: "+ingoing[loop]["i"]["expiration"]
          emI.add_field(name=ingoing[loop]["i"]["challenged"], value = expiration, inline=False)
      if loop == -1:
        emI.add_field(name="Sorry, there's nothing incoming.", value = "Maybe get some more frenemies? OR GO PRACTICE.")
      msg = await ctx.send(embed=emI)
      sent = 0
      await msg.add_reaction("▶️")
      try:
        while str(sent).isnumeric() == True:
          answer = await self.bot.wait_for('reaction_add', check= lambda reaction, user: user.id ==ctx.author.id, timeout=60)
          if str(answer[0]) in str(liszt):
            if sent == 0:
              await msg.edit(embed=emO)
              sent = 1
            else:
              await msg.edit(embed=emI)
              sent = 0
          await msg.remove_reaction(answer[0], answer[1])
      except asyncio.TimeoutError:
        pass
  
  @mailbox.error
  async def mail_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(f"Wait {round(error.retry_after,3)} seconds. I sichuan your pepper!!")
    else:
      raise error


  @commands.command(brief = "Play a team game.", description = "Play a team game.")
  async def game(self, ctx):
    pieces = ["https://imgur.com/ap3xhAx.png","https://imgur.com/YlXwca6.png","https://imgur.com/bAzulbm.png","https://imgur.com/rTy01R7.png","https://imgur.com/XK1N3v6.png","https://imgur.com/Uq77WqN.png","https://imgur.com/QlRRgZa.png","https://imgur.com/kEw5Xy5.png", "https://imgur.com/vHYfksw.png", "https://imgur.com/ATa2JNN.png", "https://imgur.com/oWVIRWT.png"]
    allEra = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣']
    era = ['5️⃣', '4️⃣', '3️⃣', '4️⃣', '2️⃣', '5️⃣', '4️⃣', '4️⃣','2️⃣','3️⃣','5️⃣']
    composer = ["rachmaninoff", "schubert", "mozart", "bizet", "bach", "stravinsky", "smetana", "bazzini", "handel", "mozart", "copland"]
    typeOfPiece = ["duet", "duet", "symphony", "symphony", "solo", "symphony", "symphony", "solo", "other","symphony", "symphony", "other"]
    piece, temp = random.randint(0,10), getUserData(ctx.author.id)
    tem = temp["team"]
    if tem == "None":
      await ctx.send("You're not part of a team!")
      return
    temp = getTeamData(tem)
    timeLast = temp["gamed"]
    utcNow = pytz.utc.localize(datetime.datetime.utcnow())
    checkCooldown = timeLast + timedelta(hours=12)
    d = utcNow.replace(tzinfo=None)
    if d < checkCooldown:
      await ctx.send(f"Your team has played this game in the last twelve hours lah! Wait {checkCooldown-d} hours lah!")
      return
    else:
      teamData.update_one({"tn": tem}, {"$set": {"gamed": d}})
    validMembers, points, questionsRight = temp["members"], 0, 0
    em = discord.Embed(title = "Question 1 - Guess the era of the piece shown.", description = "Reactions from left to right, renaissance, baroque, classical, romantic, 20th century, contemporary.",color = 15417396)
    em.set_image(url=pieces[piece])
    em.set_footer(text=f"You have 6 minutes to finish the game as a team {tem}.")
    msg = await ctx.send(embed=em)
    for any in allEra:
      await msg.add_reaction(any)
    try:
      answer = await self.bot.wait_for('reaction_add', check= lambda reaction, user: user.id in validMembers, timeout=600)
      while str(answer[0]) not in str(allEra):
        answer = await self.bot.wait_for('reaction_add', check= lambda reaction, user: user.id in validMembers)
      if str(answer[0]) == str(era[piece]):
        points += 1
        questionsRight += 1
      await msg.remove_reaction(answer[0], answer[1])
      em = discord.Embed(title = "Question 2 - Guess the composer of the piece, by last name.", description = "Send it in a message, beginning with 'a: '", color = 15417396)
      em.set_image(url=pieces[piece])
      em.set_footer(text=f"You have 6 minutes to finish the game as a team {tem}.")
      await ctx.send(embed=em)
      Answer = await self.bot.wait_for('message', check = lambda message: message.author.id in validMembers)
      while Answer.content.lower().startswith("a: ") == False:
        Answer = await self.bot.wait_for('message', check = lambda message: message.author.id in validMembers)
      if str(Answer.content.lower()[3:]) == str(composer[piece]):
        points += 3
        questionsRight += 1
      await Answer.delete()
      del Answer
      em = discord.Embed(title = "Question 3 - What type of piece was it originally?", description = "Valid answers are solo, concerto, symphony, concert band, jazz band, string orchestra, duet, trio, quartet, quintet, and other. Send it in a message, beginning with 'a: '", color = 15417396)
      em.set_image(url=pieces[piece])
      em.set_footer(text=f"You have 6 minutes to finish the game as a team {tem}.")
      await ctx.send(embed=em)
      Answer = await self.bot.wait_for('message', check = lambda message: message.author.id in validMembers)
      while Answer.content.lower().startswith("a: ") == False:
        Answer = await self.bot.wait_for('message', check = lambda message: message.author.id in validMembers)
      if str(Answer.content.lower()[3:]) == str(typeOfPiece[piece]):
        points += 3
        questionsRight += 1
      await Answer.delete()
      current = temp["xp"] + points
      #Need to check if team has done a quest for the day
      if temp["qname"] == "None" or points == 0:
        pass
      else:
        tg = temp["qprog"][0]["tg"]+1
        print(tg)
        teamData.update_one({"tn": temp["tn"]}, {"$push": {"qprog": {"days":temp["qprog"][0]["days"], "pday": temp["qprog"][0]["pday"], "pdone": temp["qprog"][0]["pdone"],"pcont": temp["qprog"][0]["pcont"], "tg": tg, "bb": temp["qprog"][0]["bb"]}}})
        teamData.update_one({"tn": temp["tn"]}, {"$pull": {"qprog": {"days":temp["qprog"][0]["days"], "pday": temp["qprog"][0]["pday"], "pdone": temp["qprog"][0]["pdone"],"pcont": temp["qprog"][0]["pcont"], "tg": temp["qprog"][0]["tg"], "bb": temp["qprog"][0]["bb"]}}})
        reee= checkQuest(temp["tn"])
        if reee is None:
          pass
        else:
          await ctx.send(f"*'{reee[0]}'*\nHuzzah! Your team has finished a quest by playing games. Huh. Each member of your team is rewarded with {reee[1]} <:bubbletea:818865910034071572>. NOW GO PRACTICE LAH!")
      teamData.update_one({"tn": tem}, {"$set" :{"xp": current}})
      await ctx.send(f"Your team got {questionsRight} questions correct, gaining {points} xp.")
    except asyncio.TimeoutError:
      await ctx.send(f"You too slow lah! Game over with {points} points.")

  @commands.command(aliases = ["bq"], brief = "Embark on a quest.", description = "Embark on a quest, setting your difficulty as either easy, medium, or hard (or have it randomized).")
  @commands.cooldown(1, 3600, commands.BucketType.user)
  async def bquest(self, ctx, difficulty = None):
    temp = getUserData(ctx.author.id)
    hasTeam = temp["team"]
    if hasTeam == "None":
      await ctx.send("You're not part of a team lah!")
      return
    team = getTeamData(hasTeam)
    currentQuest = team["qname"]
    if currentQuest != "None":
      await ctx.send("Your team is already on a quest.")
      return
    difficulties = ["Easy", "Easy", "Easy", "Easy", "Easy", "Medium", "Medium", "Hard"]
    members = len(team["members"])
    if difficulty is None:
      difficulty = random.choice(difficulties)
    if str(difficulty).lower() == "easy" or str(difficulty).lower() == "e":
      difficulty = "Easy"
      members = math.floor(members*0.3) 
      t = 10
      col = 4373885
    elif str(difficulty).lower() == "medium" or str(difficulty).lower() == "m":
      difficulty = "Medium"
      members = math.floor(members*0.5)
      t= 30
      col =	16768122
    elif str(difficulty).lower() == "hard" or str(difficulty).lower() == "h":
      difficulty = "Hard"
      members = math.floor(members*.8)
      t=60
      col = 15417396
    else:
      await ctx.send("Invalid argument lah! I mapo your tofu lah!")
      return
      ctx.command.reset_cooldown(ctx)
    if members == 0:
      members = 1
    with open('cogs/media/quests.json') as f:
      data = json.load(f)
    f.close()
    storm = list(data.keys())
    questChoice = []
    for x in storm:
      if data[x]["Difficulty"] == difficulty:
        questChoice.append(x)
    choices = random.choice(questChoice)
    choice = difficulty[:1]+choices
    teamData.update_one({"tn": hasTeam}, {"$set":{"qname": choice}})
    teamData.update_one({"tn": hasTeam}, {"$push": {"qreq": {"days": data[choices]["DaysReq"], "pN": members, "tg": data[choices]["TeamGames"], "bb": data[choices]["BBNeeded"]}}})
    teamData.update_one({"tn": hasTeam}, {"$push": {"qprog": {"days": 0, "pday": 0, "pdone": "12 July 2012","pcont": "", "tg": 0, "bb": 0}}})
    em = discord.Embed(title = f"`NEW QUEST:` {choices}", description = data[choices]["StartText"], color = col)
    em.set_thumbnail(url="https://www.kindpng.com/picc/m/340-3406738_scroll-icon-png-transparent-png.png")
    em.add_field(name="Difficulty", value=difficulty, inline=False)
    em.add_field(name="Days required", value=data[choices]["DaysReq"], inline=True)
    if data[choices]["TeamGames"] != 0:
      em.add_field(name="Games required", value=data[choices]["TeamGames"], inline=True)
    if data[choices]["BBNeeded"] != 0:
      em.add_field(name="Bubble Tea required:", value=data[choices]["BBNeeded"], inline=True)
    em.set_footer(text ="Go practice lah! ⏰")
    await ctx.send(embed=em)
  @commands.command(aliases=["dq","displayq","displayquest","showquest","squest"], brief="Displays team's current quest", description = "Displays a team's progress on their current quest. Cooldown time: 10 minutes.")
  @commands.cooldown(1, 600, commands.BucketType.user)
  async def dquest(self, ctx):
    temp = getUserData(ctx.author.id)
    hasTeam = temp["team"]
    if hasTeam == "None":
      await ctx.send("You're not part of a team lah!")
      return
    team = getTeamData(hasTeam)
    currentQuest = team["qname"]
    if currentQuest == "None":
      await ctx.send("Your team is not on a quest.")
      return
    diff = team["qname"][:1]
    if diff == "E":
      diff = 4373885
      difficulty = "Easy"
    elif diff == "M":
      diff = 16768122
      difficulty = "Medium"
    else:
      diff = 15417396
      difficulty = "Hard"
    name = team["qname"][1:]
    line1= ""
    for x in range(1,len(name)+7):
      line1 += "─"
    em = discord.Embed(title=f"Current quest: {name}", description = line1, color = diff)
    em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    em.add_field(name="Difficulty", value=difficulty, inline=False)
    val =team["qprog"][0]["days"]
    val2=team["qreq"][0]["days"]
    em.add_field(name="Days required", value=f"{val}/{val2}", inline=True)
    if team["qreq"][0]["tg"] != 0:
      val =team["qprog"][0]["tg"]
      val2=team["qreq"][0]["tg"]
      em.add_field(name="Games required", value=f"{val}/{val2}",inline=True)
    if team["qreq"][0]["bb"] != 0:
      val =team["qprog"][0]["bb"]
      val2=team["qreq"][0]["bb"]
      em.add_field(name="Bubble Tea required:", value=f"{val}/{val2}", inline=True)
    await ctx.send(embed=em)

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


#Helper function uwu
def getUserData(x):
  userTeam = userData.find_one({"id": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "to-do": [], "to-done": [],"practiceLog": [], "practiceGoal": 0, "dailyLastCollected": d, "streak": 0, "instrument": [], "clef": 0}
    userData.insert_one(newUser)
  userTeam = userData.find_one({"id": x})
  return userTeam 
  
def getTeamData(x):
  userTeam = teamData.find_one({"tn": x})
  if userTeam is None:
    newTeam = {"tn": x, "xp": 0, "qname": "None", "qreq": [], "qprog": [], "gamed": 0, "members": [], "captains": [], "bans": [], "pending": [], "challenges": [], "accepted": [],"stats": []}
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
          teamData.update_one({"tn": x["tn"]}, {"$pull": {"qprog": {"days":x["qprog"][0]["days"], "pday": x["qprog"][0]["pday"], "pdone": x["qprog"][0]["pdone"],"pcont": x["qprog"][0]["pcont"], "tg": x["qprog"][0]["tg"], "bb": x["qprog"][0]["bb"]}}})
          teamData.update_one({"tn": x["tn"]}, {"$pull": {"qreq": {"days": x["qreq"][0]["days"], "pN": x["qreq"][0]["pN"], "tg": x["qreq"][0]["tg"], "bb": x["qreq"][0]["bb"]}}})
          teamData.update_one({"tn":x["tn"]}, {"$set": {"qname": "None"}})
          return [data[title]["FinishText"],amount]
  teamData.update_one({"tn": x["tn"]}, {"$push": {"qprog": {"days":daysOld, "pday": x["qprog"][0]["pday"], "pdone": timeNow,"pcont": contributors, "tg": tGames, "bb": x["qprog"][0]["bb"]}}})
  teamData.update_one({"tn": x["tn"]}, {"$pull": {"qprog": {"days":x["qprog"][0]["days"], "pday": x["qprog"][0]["pday"], "pdone": x["qprog"][0]["pdone"],"pcont": x["qprog"][0]["pcont"], "tg": x["qprog"][0]["tg"], "bb": x["qprog"][0]["bb"]}}})
  return
def setup(bot):
  bot.add_cog(Teams(bot))
