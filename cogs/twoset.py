#Tracks r/lingling40hrs and probably other music subreddit submissions, Twoset vids, etc.
import praw
import discord
from discord.ext import commands
import os
import random
import dns
import TenGiphPy

#Sets up API, https://www.reddit.com/prefs/apps.
reddit = praw.Reddit(client_id=os.getenv('CLIENTID'), client_secret=os.getenv('SECRET'), user_agent="The_Nights_Fall")
tenor = TenGiphPy.Tenor(token=os.getenv('TENORKEY'))
giphy = TenGiphPy.Giphy(token=os.getenv('GIPHYKEY'))

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

  @commands.command(aliases = ["twosetmeme", "meme"], brief = "Sends a TwoSet Meme.", description = "Sends a TwoSet Meme.")
  async def tsmeme(self, ctx):
    content = tenor.random("twoset")
    em = discord.Embed(title="Meme from Tenor :)")
    em.set_image(url=content)
    em.set_footer(text="Don't like the gifs? I don't control them so...")
    await ctx.send(embed = em)
  
  @commands.command(aliases = ["socials"], brief="Gets a list of TwoSet's social media accounts.", description = "Gets a list of TwoSet's social media accounts")
  async def tssocials(self, ctx):
    em = discord.Embed(title="TwoSet social links")
    em.set_thumbnail(url="https://i.pinimg.com/originals/95/7c/27/957c2719b2863d68ae147164d0f4b19a.jpg")
    em.add_field(name="YT", value="[Link](https://youtube.com/c/twosetviolin/videos)")
    em.add_field(name="TikTok", value="[Link](https://www.tiktok.com/@twosetviolin?lang=en)", inline=False)
    em.add_field(name="Instagram", value="[Link](https://www.instagram.com/twosetviolin/?hl=en)", inline=False)
    em.add_field(name="Twitter", value = "[Link](https://twitter.com/TwoSetViolin?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor)", inline=False)
    em.add_field(name="Facebook", value="[Link](https://www.facebook.com/TwoSetViolin)", inline=False)
    em.set_footer(text="Missed anything? DM Nights!")
    await ctx.send(embed =em)
#Probably have interesting and AMAZING here. As well as some other sacreligious memes.
def setup(bot):
  bot.add_cog(Twoset(bot))