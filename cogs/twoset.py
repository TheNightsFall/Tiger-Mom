#Tracks r/lingling40hrs and probably other music subreddit submissions, Twoset vids, etc.
import praw
import discord
from discord.ext import commands
import os
import random
import dns
from PIL import Image, ImageFont, ImageDraw
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
    desc = '''----------------------------------------------------------
       [YouTube](https://youtube.com/c/twosetviolin/videos)
       [TikTok](https://www.tiktok.com/@twosetviolin?lang=en)
       [Instagram](https://www.instagram.com/twosetviolin/?hl=en)
       [Twitter](https://twitter.com/TwoSetViolin?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor)
       [Facebook](https://www.facebook.com/TwoSetViolin)
       [Personal website](https://www.twosetviolin.com/)
       ----------------------------------------------------------
       [r/lingling40hrs](https://www.reddit.com/r/lingling40hrs/)
       [TwoSetApparel](https://twosetapparel.com/)
       ----------------------------------------------------------
       "TwoSet Violin – founded in 2014 by Australian duo Brett Yang and Eddy Chen – first went viral with their funny and sometimes painfully accurate videos depicting life as a classical musician. With over 5,000,000 followers across social media and over one billion views, TwoSet inspires musicians worldwide with humor and a relatable ‘imperfectness.’"

          - From their website
       '''
    em = discord.Embed(title="TwoSet social links", description = desc, color = 0)
    em.set_thumbnail(url="https://i.pinimg.com/originals/95/7c/27/957c2719b2863d68ae147164d0f4b19a.jpg")
    em.set_footer(text="⏰ Have you practiced?")
    await ctx.send(embed = em)
  
  @commands.command(brief = "iNtErEstInG.", description = "iNtErEstInG.")
  async def interesting(self, ctx, user:discord.Member = None):
    if user == None:
      user = ctx.author
    interest = Image.open("cogs/media/0.jpg")
    font = ImageFont.truetype("cogs/media/Monaco.ttf", 80)
    draw = ImageDraw.Draw(interest)
    draw.text((101,490),f"{user.display_name} is",(255,255,255), font=font)
    interest.save("cogs/media/01.jpg")
    await ctx.send(content = f"{user.display_name} is iNteReSTiNG", file=discord.File("cogs/media/01.jpg"))
#Probably have interesting and AMAZING here. As well as some other sacreligious memes.
def setup(bot):
  bot.add_cog(Twoset(bot))