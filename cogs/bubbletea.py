#Glossary of music concepts in embeds, eh.

#Hangman, unscramble the word
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

cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]
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
    checkStreak = dailyLast + timedelta(days=2)
    checkCooldown = dailyLast + timedelta(days=1)
    d = utcNow.replace(tzinfo=None)
    if checkStreak <= d:
      newBal = currentBal+baseReward
      userData.update_one({"id":ctx.author.id}, {"$set":{"streak":0}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"dailyLastCollected": utcNow}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": newBal}})
      await ctx.send(f"You received {baseReward} <:bubbletea:818865910034071572>. Come back in 24 hours.")
    elif checkCooldown > d:
      await ctx.send("Stop trying to collect dailies more than once. I kungpao your chicken!")
    else:
      newStreak = user["streak"]+1
      earnings = baseReward + newStreak*5
      newBal = currentBal+earnings
      userData.update_one({"id":ctx.author.id}, {"$set":{"streak":newStreak}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"dailyLastCollected": utcNow}})
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": newBal}})
      await ctx.send(f"You received {earnings} <:bubbletea:818865910034071572>. Come back in 24 hours.")
  
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
    noteList = {"C":260, "D":249, "E": 234, "F":217, "G":202,"A":184,"B":169,"c":151,"d":136,"e":119,"f":104,"g":87,}
    vals = list(noteList.values())
    keys = list(noteList.keys())
    stave = Image.open("cogs/media/notes/trebleclef.jpg")
    picker = random.randint(1,3)
    if picker == 1:
      note = Image.open("cogs/media/notes/wholenoteline.png")
      note = note.resize((68,30))
      yValueChoice = [260, 234, 202, 169, 136, 104]
    else:
      note = Image.open("cogs/media/notes/wholenote.png")
      note = note.resize((47,29))
      yValueChoice = [249, 217, 184, 151, 119, 87]
    yValue=random.choice(yValueChoice)
    pos = vals.index(yValue)
    correctNote = keys[pos].upper()
    stave.paste(note, (330,yValue))
    stave.save("cogs/media/notes/notereading.jpg")
    em = discord.Embed(title="Identify the note!", color = 15417396)
    file = discord.File("cogs/media/notes/notereading.jpg", filename = "image.jpg")
    em.set_image(url="attachment://image.png")
    user = getUserData(ctx.author.id)
    bal = user["bubbleTea"]
    try:
      await ctx.send(file=file, embed=em)
      answer = await self.bot.wait_for('message', check= lambda message: message.author == ctx.author, timeout=10)
      if answer.content.upper() == correctNote:
        await answer.add_reaction("🎯")
        await ctx.send("Correct, but Ling ling got it while doing brain surgery. +5 <:bubbletea:818865910034071572>")
        bal = bal + 5 if bal != 0 else 5 #Does this work if I do +=?
        userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
      else:
        await ctx.send(f"Incorrect! The right note was {correctNote}. -5 <:bubbletea:818865910034071572>")
        bal = bal - 5 if bal - 5 >= 0 else 0
        userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
    except asyncio.TimeoutError:
      await ctx.send(f"You too slow lah! Correct answer is {correctNote}. -3 <:bubbletea:818865910034071572>")
      bal = bal - 3 if bal - 3 >= 0 else 0
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})

  @noteReading.error
  async def noteReading_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(f"Wait {round(error.retry_after,3)} seconds. I sichuan your pepper!!")
    else:
      raise error

  @commands.command(aliases = ["composers"], brief = "Hangman...but with bubble tea.", description = "Hangman...but with bubble tea.")
  @commands.cooldown(1, 20, commands.BucketType.user)
  async def hangman(self, ctx):
    global composers
    user = getUserData(ctx.author.id)
    bal = user["bubbleTea"]
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
        while letter.content.isalpha() == False or len(letter.content) != 1:
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
              await ctx.send(embed = em)
              break
        else:
          pass
      except asyncio.TimeoutError:
        await ctx.send(f"You lose lah! Too slow! Word was {word.capitalize()}.")
        break
  
  @hangman.error
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
      return

    if era[pick] in answer.content:
      await answer.add_reaction("🎯")
      await ctx.send("Correct, but Ling ling got it while doing brain surgery. +5 <:bubbletea:818865910034071572>")
      bal = bal + 5 if bal != 0 else 5
      userData.update_one({"id":ctx.author.id}, {"$set":{"bubbleTea": bal}})
    else:
      await ctx.send("Incorrect lah! -5 <:bubbletea:818865910034071572>")
      bal = bal - 5 if bal > 5 else 0
      userData.update_one({"id":ctx.author.id}, {"$set": {"bubbleTea": bal}})

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

def getUserData(x):
  userTeam = userData.find_one({"id": x})
  d = datetime.datetime.strptime("1919-10-13.000Z","%Y-%m-%d.000Z")
  if userTeam is None:
    newUser = {"id": x, "practiceTime": 0, "bubbleTea": 0, "team": "None", "streak": 0, "to-do": [], "practiceLog": [],"sprintRemaining": -10, "dailyLastCollected": d,"practiceGoal": 0, "to-done": [], "awards": []}
    userData.insert_one(newUser)
  userTeam = userData.find_one({"id": x})
  return userTeam 


def setup(bot):
  bot.add_cog(BubbleTea(bot))