#Tracks r/lingling40hrs and probably other music subreddit submissions, Twoset vids, etc.
import praw
import discord
from discord.ext import commands
import os
import random
import dns

#Sets up API, https://www.reddit.com/prefs/apps.
reddit = praw.Reddit(client_id=os.getenv('CLIENTID'), client_secret=os.getenv('SECRET'), user_agent="The_Nights_Fall")

class Twoset(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  #Ling ling already doctor lah. Meanwhile you still here making bot. 哎呀！
  @commands.command(brief = "Ling ling already ____ lah!", description = "Ling ling already ____ lah!")
  async def lingling(self, ctx, prodigy = None):
    prodigy = "doctor" if prodigy is None else prodigy
    await ctx.send(f"Ling ling already {prodigy} lah! What you be, {ctx.author.mention}? Hah?")


  @commands.command(aliases = ["tsr", "lingling40hrs"], brief = "Gets a post from r/lingling40hrs.", description = "Gets a post from r/lingling40hrs.")
  async def twosetreddit(self, ctx):
    submissions = reddit.subreddit('lingling40hrs').hot()
    keepParsing = 1
    #While loop runs until it finds an image post
    while keepParsing == 1:
      postPick = random.randint(1, 50)
      for i in range(0, postPick):
        submission = next(x for x in submissions if not x.stickied)
        if submission.url.endswith('.jpg') or submission.url.endswith('.png'):
          keepParsing = 0
        else: 
          keepParsing = 1
    em = discord.Embed(title=submission.title, url = "https://reddit.com"+submission.permalink, description=f"By: u/{submission.author} in r/lingling40hrs", color=16733952)
    em.set_image(url= submission.url)
    em.set_footer(text=f"🔼 {submission.score} 💬 {submission.num_comments}")
    await ctx.send(embed = em)

#Probably have interesting and AMAZING here. As well as some other sacreligious memes.
def setup(bot):
  bot.add_cog(Twoset(bot))