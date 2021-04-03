'''
import dns
import os
import pymongo
import discord
from discord.ext import commands
import discord.utils
import youtube_dl
import time
import pafy

cluster = pymongo.MongoClient(os.getenv('THING'))
guildData = cluster["tigermom"]["guilds"]
userData = cluster["tigermom"]["userstats"]
queueLink = []
queue = []

class Listening(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  #All the music commands
  #I have to redo all this with databases, using push and pop.
  @commands.command(brief = "Plays a piece.", description = "Plays a piece.")
  async def play(self, ctx, url: str = None):
    guild = getGuildData(ctx.guild.id)
    queueLink = guild["queuelink"]
    if url is None:
      await ctx.send("You need a url lah!")
      return
    else:
      pass
    vc = ctx.author.voice
    voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    #try:
    if [] == queueLink: #Should work?
      qquestion = 0
      guildData.update_one({"id": ctx.guild.id}, {"$push" :{"queuelink": url}})
      video = pafy.new(url)
      title = video.title+", by "+video.author
      guildData.update_one({"id": ctx.guild.id}, {"$push" :{"queue": title}})
      getMusic(url, title)
    else:
      qquestion = 1
      guildData.update_one({"id": ctx.guild.id}, {"$push" :{"queuelink": url}})
      video = pafy.new(url)
      title = video.title
      guildData.update_one({"id": ctx.guild.id}, {"$push" :{"queue": title}})
        
        #Connects.
    try:
      voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
      if voice is None:
        await vc.channel.connect()
      voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
      if qquestion == 0:
        voice.play(discord.FFmpegPCMAudio(f"{title}.mp3"))
    except:
      em = discord.Embed(title="Unable to join vc lah, or you're not in one!", color = 16092072)
      await ctx.send(embed=em)
    if queueLink:
      em = discord.Embed(title = "Queued song.", color = 16092072)
      await ctx.send(embed=em)
          #Here will be loop for playing queued stuff
    queueLink = guild["queuelink"]
    for x in queueLink:
      while vc.is_playing() or vc.is_paused():
        time.sleep(1)
     
      print("run.")
      guildData.update_one({"id": ctx.guild.id}, {"$pop": {"queue": -1}})
      guildData.update_one({"id": ctx.guild.id}, {"$pop": {"queuelink": -1}})
      queueLink = guild["queuelink"]
      getMusic(url,title)
      voice.play(discord.FFmpegPCMAudio(f"{title}.mp3"))
    except:
        em = discord.Embed(title="Something went wrong, or your url wasn't valid", color = 16092072)
        await ctx.send(embed=em)
        return
        

  @commands.command(brief = "Leaves VC.", description = "Leaves VC.")
  async def leave(self, ctx):
    global queueLink
    global queue
    try:
      vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
      if vc.is_connected():
        await vc.disconnect()
        queueLink = []
        queue = []
      else:
        await ctx.send("Not connected lah! Stop messing around and go practice!")
    except:
      await ctx.send("Not connected lah!")

  @commands.command(brief = "Pause a piece.", description = "Pause a piece.")
  async def pause(self, ctx):
    vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    if vc.is_playing():
      vc.pause()
    elif not vc.is_connected():
      await ctx.send("Not in VC.")
    else:
      await ctx.send("Music already paused lah! Why you not practicing?")
  
  @commands.command(brief = "Resume a piece.", description = "Resume a piece.")
  async def resume(self, ctx):
    vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    if vc.is_paused():
      vc.resume()
    elif not vc.is_connected():
      await ctx.send("Not in VC.")
    else:
      await ctx.send("Audio not paused.")

  @commands.command(brief = "View queue.", description = "View queue.")
  async def queue(self, ctx):
    pass

def getGuildData(x):
  guildTeam = guildData.find_one({"id":x})
  if guildTeam is None:
    newGuild = {"id": x, "queue": [], "queuelink": []}
    guildData.insert_one(newGuild)
  guildTeam = guildData.find_one({"id":x})
  return guildTeam

def getMusic(x,t):
  ydl_opts = {
      'format': 'bestaudio/best',
      #'outtmpl': 'cogs/',
      'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
      }]
    }
  songThere = os.path.isfile("song.mp3")
  if songThere:
    os.remove("song.mp3")
  #Downloads YT vid
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([x])
  #Changes name to song.mp3, deletes video file that comes along
  for file in os.listdir("/home/runner/Tiger-Mom"):
    if file.endswith("mp3"):
      os.rename(file, f"{t}.mp3")
    if file.endswith(".webm") or file.endswith(".m4a"):
      os.remove(file)

def getGuildData(x):
  guildTeam = guildData.find_one({"id":x})
  if guildTeam is None:
    newGuild = {"id": x, "queue": [], "queuelink": []}
    guildData.insert_one(newGuild)
  guildTeam = guildData.find_one({"id":x})
  return guildTeam
#def setup(bot):
#  bot.add_cog(Listening(bot))
'''