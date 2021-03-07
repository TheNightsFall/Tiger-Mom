import discord
import dns
import os
import pymongo
from discord.ext import commands
import datetime
from dateutil import tz

cluster = pymongo.MongoClient(os.getenv('THING'))
userData = cluster["tigermom"]["userstats"]

class Practice(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  async def log(self, ctx, amountPracticed = None):
    if amountPracticed == None:
      await ctx.send("WHAT? No practice? I mapo your tofu tonight!")

def setup(bot):
  bot.add_cog(Practice(bot))