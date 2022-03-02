import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        pass

def setup(bot: commands.Bot):
    bot.add_cog(ExampleCog(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog("ExampleCog")