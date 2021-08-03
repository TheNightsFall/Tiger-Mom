#Glossary of music concepts in embeds, eh.

#Hangman, unscramble the word
#get_user()
import dns
import os
import pymongo
import discord
from discord.ext import commands
import datetime
from datetime import timedelta
import pytz
from PIL import Image
import random
import asyncio
import json

cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]
teamData = cluster["tigermom"]["teams"]
composers = ["Bach", "Beethoven", "Mendelssohn","Mozart", "Sibelius", "Tchaikovsky", "Prokofiev", "Chopin", "Liszt", "Rachmaninoff", "Paganini", "Bingen", "Monteverdi", "Handel","Vivaldi", "Debussy", "Haydn", "Schumann", "Elgar", "Verdi","Wagner", "Strauss", "Mahler", "Schubert", "Stravinsky","Shostakovich","Brahms", "Holst", "Smetana", "Dvorak","Glass", "Bernstein", "Cage", "Boulez", "Satie", "Berg", "Gershwin", "Copland", "Schoenberg", "Bartok","Britten","Ravel"]

class BubbleTea(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief = "Daily reward.", description = "Daily reward.")
  @commands.cooldown(1, 86400, commands.BucketType.user)
  async def daily(self, ctx):
    baseReward = 75
    user = getUserData(ctx.author.id)
    utcNow = pytz.utc.localize(datetime.datetime.utcnow())
    dailyLast = user["dailyLastCollected"]
    currentBal = user["bubbleTea"]
    tem = user["team"]
    checkStreak = dailyLast + timedelta(days=2)
    checkCooldown = dailyLast + timedelta(days=1)
    d = utcNow.replace(tzinfo=None)
    if checkStreak <= d:
      newBal = currentBal+baseReward
      addChal(tem, baseReward)
      if user["team"] != "None":
        team = getTeamData(user["team"])
        if team["qname"] != "None":
          aP = int(team["qprog"][0]["bb"])+baseReward
          teamData.update_one({"tn":team["tn"]}, {"$push": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["cont"], "tg": team["qprog"][0]["tg"], "bb": aP}}})
          teamData.update_one({"tn": team["tn"]}, {"$pull": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["pcont"], "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
          reee = checkQuest(team["tn"])
      userData.update_one({"id":ctx.author.id}, {"$set":{"streak":0}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"dailyLastCollected": utcNow}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": newBal}})
      await ctx.send(f"You received {baseReward} <:bubbletea:818865910034071572>. Come back in 24 hours.")
    elif checkCooldown > d:
      await ctx.send("Stop trying to collect dailies more than once. I kungpao your chicken!")
      reee = None
    else:
      newStreak = user["streak"]+1
      earnings = baseReward + newStreak*5
      newBal = currentBal+earnings
      addChal(tem, earnings)
      if user["team"] != "None":
        team = getTeamData(user["team"])
        if team["qname"] != "None":
          aP = int(team["qprog"][0]["bb"])+earnings
          teamData.update_one({"tn":team["tn"]}, {"$push": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["cont"], "tg": team["qprog"][0]["tg"], "bb": aP}}})
          teamData.update_one({"tn": team["tn"]}, {"$pull": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["pcont"], "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
          reee = checkQuest(team["tn"])
      userData.update_one({"id":ctx.author.id}, {"$set":{"streak":newStreak}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"dailyLastCollected": utcNow}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": newBal}})
      await ctx.send(f"You received {earnings} <:bubbletea:818865910034071572>. Come back in 24 hours.")
    if reee is None:
      pass
    else:
      await ctx.send(f"*'{reee[0]}'*\nYour team has finished a quest by playing...games. Just...just go practice. Each member of your team is rewarded with {reee[1]} <:bubbletea:818865910034071572>. ")
  @daily.error
  async def daily_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send("Stop trying to collect dailies more than once. I kungpao your chicken!")
    else:
      raise error

  #This without sharps and flats only took me *checks watch* 2.5 hours. 
  @commands.command(aliases = ["nr"], brief = "Tests your notereading abilities.", description = "Tests your notereading abilities.")
  @commands.cooldown(1, 7, commands.BucketType.user)
  async def noteReading(self, ctx):
    noteList = {"C":260, "D":249, "E": 233, "F":217, "G":201,"A":184,"B":168,"c":152,"d":136,"e":119,"f":103,"g":86,}
    vals = list(noteList.values())
    keys = list(noteList.keys())
    stave = Image.open("cogs/media/notes/trebleclef.jpg")
    picker = random.randint(1,3)
    if picker == 1:
      note = Image.open("cogs/media/notes/wholenoteline1.png")
      note = note.resize((47,28))
      yValueChoice = [260, 233, 201, 168, 136, 103]
    else:
      note = Image.open("cogs/media/notes/wholenote.png")
      note = note.resize((47,29))
      yValueChoice = [249, 217, 184, 152, 119, 86]
    yValue=random.choice(yValueChoice)
    if yValue == 217 or yValue == 152:
        note = note.resize((46,28))
    pos = vals.index(yValue)
    correctNote = keys[pos].upper()
    stave.paste(note, (330,yValue))
    stave.save("cogs/media/notes/notereading.jpg")
    em = discord.Embed(title="Identify the note!", color = 15417396)
    file = discord.File("cogs/media/notes/notereading.jpg", filename = "image.jpg")
    em.set_image(url="attachment://image.png")
    user = getUserData(ctx.author.id)
    bal = user["bubbleTea"]
    tem = user["team"]
    try:
      await ctx.send(file=file, embed=em)
      answer = await self.bot.wait_for('message', check= lambda message: message.author == ctx.author, timeout=10)
      if answer.content.upper() == correctNote:
        await answer.add_reaction("🎯")
        await ctx.send("Correct, but Ling ling got it while doing brain surgery. +5 <:bubbletea:818865910034071572>")
        bal = bal + 5 if bal != 0 else 5 #Does this work if I do +=?
        userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
        addChal(tem, 5)
        if user["team"] != "None":
          team = getTeamData(user["team"])
          if team["qname"] != "None":
            aP = int(team["qprog"][0]["bb"])+5
            teamData.update_one({"tn":team["tn"]}, {"$push": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["cont"], "tg": team["qprog"][0]["tg"], "bb": aP}}})
            teamData.update_one({"tn": team["tn"]}, {"$pull": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["pcont"], "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
            reee = checkQuest(team["tn"])
            if reee is None:
              pass
            else:
              await ctx.send(f"*'{reee[0]}'*\nYour team has finished a quest by playing...games. Just...just go practice. Each member of your team is rewarded with {reee[1]} <:bubbletea:818865910034071572>. ")
      else:
        await ctx.send(f"Incorrect! The right note was {correctNote}. -5 <:bubbletea:818865910034071572>")
        bal = bal - 5 if bal - 5 >= 0 else 0
        userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
        addChal(tem, -5)
    except asyncio.TimeoutError:
      await ctx.send(f"You too slow lah! Correct answer is {correctNote}. -3 <:bubbletea:818865910034071572>")
      bal = bal - 3 if bal - 3 >= 0 else 0
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
      addChal(tem, -3)
  @noteReading.error
  async def noteReading_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(f"Wait {round(error.retry_after,3)} seconds. I sichuan your pepper!!")
    else:
      raise error

  @commands.command(aliases = ["composers","hangman","manhang"], brief = "Hangman...but with bubble tea.", description = "Hangman...but with bubble tea.")
  @commands.cooldown(1, 20, commands.BucketType.user)
  async def hm(self, ctx):
    global composers
    user = getUserData(ctx.author.id)
    bal = user["bubbleTea"]
    tem = user["team"]
    tries = 0
    prevGuesses = ''
    wordLength = ""
    lettersGuessedWrong = ''
    stages = ["https://i.imgur.com/9rhapPT.png","https://imgur.com/ajwscmm.png","https://imgur.com/3oPGVWp.png","https://imgur.com/2T6dHKo.png","https://imgur.com/k6Gipci.png","https://imgur.com/EJJXQz6.png","https://imgur.com/vPsUnvM.png","https://imgur.com/ZiepSCT.png","https://imgur.com/Z7pMgbS.png","https://imgur.com/awakV05.png"]
    word = random.choice(composers).lower()
    temp = len(word)
    for i in range(0, temp):
      wordLength += "- "
    em = discord.Embed(title = wordLength, description = "Wrong letters: "+lettersGuessedWrong, color = 15417396)
    em.set_image(url=stages[tries])
    await ctx.send(embed = em)
    while tries < 9 and prevGuesses != "WE WIN THESE":
      try:
        letter = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 20)
        while letter.content.isalpha() == False:
          try:
            letter = await self.bot.wait_for('message', check= lambda message: message.author == ctx.author, timeout=20)
          except asyncio.TimeoutError:
            break
        if len(letter.content) == 1:
          if letter.content.lower() in prevGuesses:
            await ctx.send("You already guessed that letter lah!")
          else:
            prevGuesses += letter.content+", "
            letterPresent = [pos for pos, char in enumerate(word) if char == letter.content]
            if not letterPresent:
              tries += 1
              lettersGuessedWrong += letter.content
            else:
              wordLengthTemp = [wordLength[i:i+2] for i in range(0,len(wordLength), 2)]
              for i in letterPresent:
                wordLengthTemp[i] = letter.content+ " "
                wordLength = ''.join(map(str,wordLengthTemp))
            if tries == 9:
              em = discord.Embed(title=f"You lose lah! Word was {word.capitalize()}", description = "Wrong letters: "+lettersGuessedWrong, color = 15417396)
              em.set_footer(text="You lose 10 bubble tea.")
              em.set_image(url=stages[tries])
              await ctx.send(embed = em)
              bal = bal-10 if bal >= 10 else 0
              userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
              addChal(tem, -10)
              break
            elif "-" in wordLength:
              em = discord.Embed(title = wordLength, description = "Wrong letters: "+lettersGuessedWrong, color = 15417396)
              em.set_image(url=stages[tries])
              await ctx.send(embed = em)
            else:
              gain = 10-tries
              em = discord.Embed(title = f"Correct! Word was {word.capitalize()}!", description = "Wrong letters: "+lettersGuessedWrong, color = 15417396)
              em.set_image(url=stages[tries])
              em.set_footer(text=f"You gain {gain} bubble tea")
              bal += gain if bal != 0 else gain
              userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
              addChal(tem, gain)
              await ctx.send(embed = em)
              if user["team"] != "None":
                team = getTeamData(user["team"])
                if team["qname"] != "None":
                  aP = int(team["qprog"][0]["bb"])+gain
                  teamData.update_one({"tn":team["tn"]}, {"$push": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["cont"], "tg": team["qprog"][0]["tg"], "bb": aP}}})
                  teamData.update_one({"tn": team["tn"]}, {"$pull": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["pcont"], "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
                  reee = checkQuest(team["tn"])
                  if reee is None:
                    pass
                  else:
                    await ctx.send(f"*'{reee[0]}'*\nYour team has finished a quest by playing...games. Just...just go practice. Each member of your team is rewarded with {reee[1]} <:bubbletea:818865910034071572>. ")
              break
        elif letter.content.lower() == word:
          gain = 10-tries
          em = discord.Embed(title = f"Correct! Word was {word.capitalize()}!", description = "Wrong letters: "+lettersGuessedWrong, color = 15417396)
          em.set_image(url=stages[tries])
          em.set_footer(text=f"You gain {gain} bubble tea")
          bal += gain if bal != 0 else gain
          userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
          addChal(tem, gain)
          await ctx.send(embed = em)
          if user["team"] != "None":
            team = getTeamData(user["team"])
            if team["qname"] != "None":
              aP = int(team["qprog"][0]["bb"])+gain
              teamData.update_one({"tn":team["tn"]}, {"$push": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["cont"], "tg": team["qprog"][0]["tg"], "bb": aP}}})
              teamData.update_one({"tn": team["tn"]}, {"$pull": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["pcont"], "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
              reee = checkQuest(team["tn"])
              if reee is None:
                pass
              else:
                await ctx.send(f"*'{reee[0]}'*\nYour team has finished a quest by playing...games. Just...just go practice. Each member of your team is rewarded with {reee[1]} <:bubbletea:818865910034071572>. ")
          break
      except asyncio.TimeoutError:
        await ctx.send(f"You lose lah! Too slow! Word was {word.capitalize()}.")
        break
  
  @hm.error
  async def hangman(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(f"Wait {round(error.retry_after,3)} seconds. I sichuan your pepper!!")
    else:
      raise error

  @commands.command(brief = "Guess the era of a composer.", description = "Guess the era of a composer.")
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def era(self, ctx):
    user = getUserData(ctx.author.id)
    bal = user["bubbleTea"]
    tem = user["team"]
    global composers
    #medieval baroque classical romantic contemporary, do in
    era = ["2","34","4","3","4","4",'5','4','4','4','4','1','1','2','2','4','3','4','4','4','4','4','4','34','45','5','4','4','4','4','5','5','5','5','45','4','5','5','5','5','5','5']
    pick = random.randint(1,len(era))
    content = "What era was "+composers[pick]+" from?"''' Type your response as a number:
    1: Medieval
    2: Baroque
    3: Classical
    4: Romantic
    5: Contemporary 
    
    You have ten seconds to answer.'''
    await ctx.send(content)
    try:
      answer = await self.bot.wait_for('message', check= lambda message: message.author == ctx.author, timeout=10)
    except:
      await ctx.send("Time's up! -3 <:bubbletea:818865910034071572>")
      bal = bal - 3 if bal > 3 else 0
      userData.update_one({"id":ctx.author.id}, {"$set": {"bubbleTea": bal}})
      addChal(tem, -3)
      return

    if era[pick] in answer.content:
      await answer.add_reaction("🎯")
      await ctx.send("Correct, but Ling ling got it while doing brain surgery. +5 <:bubbletea:818865910034071572>")
      bal = bal + 5 if bal != 0 else 5
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
      addChal(tem, 5)
      if user["team"] != "None":
        team = getTeamData(user["team"])
        if team["qname"] != "None":
          aP = int(team["qprog"][0]["bb"])+5
          teamData.update_one({"tn":team["tn"]}, {"$push": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["cont"], "tg": team["qprog"][0]["tg"], "bb": aP}}})
          teamData.update_one({"tn": team["tn"]}, {"$pull": {"qprog": {"days":team["qprog"][0]["days"], "pday": team["qprog"][0]["pday"], "pdone": team["qprog"][0]["pdone"],"pcont": team["qprog"][0]["pcont"], "tg": team["qprog"][0]["tg"], "bb": team["qprog"][0]["bb"]}}})
          reee = checkQuest(team["tn"])
          if reee is None:
            pass
          else:
            await ctx.send(f"*'{reee[0]}'*\nYour team has finished a quest by playing...games. Just...just go practice. Each member of your team is rewarded with {reee[1]} <:bubbletea:818865910034071572>. ")
    else:
      await ctx.send("Incorrect lah! -5 <:bubbletea:818865910034071572>")
      bal = bal - 5 if bal > 5 else 0
      userData.update_one({"id":ctx.author.id}, {"$set": {"bubbleTea": bal}})
      addChal(tem, -5)

  @era.error
  async def era_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(f"Wait {round(error.retry_after,3)} seconds. I sichuan your pepper!!")
    else:
      raise error

  @commands.command(brief = "Displays a user's bubble tea.", description = "Displays a user's bubble tea.")
  async def bal(self, ctx, user:discord.Member = None):
    if user is None:
      user = ctx.author
      users = getUserData(user.id)
      bal = users["bubbleTea"]
    elif user == self.bot.user:
      bal = "infinite"
    else:
      users = getUserData(user.id)
      bal = users["bubbleTea"]
    await ctx.send(f"{user.mention} has {bal} bubble tea <:bubbletea:818865910034071572>")
  
  @commands.command(aliases = ["leaderboard"], brief = "Leaderboard for bubble tea.", description = "Leaderboard for bubble tea, serverwide.")
  async def lb(self, ctx, pplShown = None):
      if pplShown == None:
          pplShown = 5
      rankings = userData.find().sort("bubbleTea",-1)
      i = 1
      emptychance = 0
      em = discord.Embed(title = f"Top {pplShown} Hoarders of Bubble Tea", color = 15417396)
      em.set_thumbnail(url=ctx.guild.icon_url)
      for x in rankings:
          try:
            temp = ctx.guild.get_member(x["id"])
            temphonks = x["bubbleTea"]
            em.add_field(name=f"{i}: {temp.name}", value=f"Bubble Tea: {temphonks}", inline=False)
            i += 1
          except:
            emptychance += 1
          if i == int(pplShown)+1:
            break
      if emptychance == int(pplShown):
        em.add_field(name="No one has any bubble tea. *sigh*.", value="Use any of the commands in the bubble tea category to get started.")
      em.set_footer(text="⏰ Go practice lah!")
      await ctx.send(embed = em)

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
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newTeam = {"tn": x, "xp": 0, "qname": "None", "qreq": [], "qprog": [], "gamed": d, "members": [], "captains": [], "bans": [], "pending": [], "challenges": [], "accepted": [],"stats": []}
    teamData.insert_one(newTeam)
  userTeam = teamData.find_one({"tn": x})
  return userTeam
  
def addChal(x, y): #x must be in the format of user["team"]
  temp = getTeamData(x)
  chal = temp["accepted"][0]
  if chal != []:
    help = chal.get('bal')
    if help+y <= 0:
      help = 0
    elif help == 0:
      help = y
    else:
      help += y
    teamData.update({"tn": temp["tn"]}, {"$push": {"accepted": {"expiration": chal.get('expiration'), "challenged": chal.get('challenged'), "bal": help}}})
    teamData.update({"tn": temp["tn"]}, {"$pull": {"accepted": {"expiration": chal.get('expiration'), "challenged": chal.get('challenged'), "bal": chal.get('bal')}}})

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

def setup(bot):
  bot.add_cog(BubbleTea(bot))