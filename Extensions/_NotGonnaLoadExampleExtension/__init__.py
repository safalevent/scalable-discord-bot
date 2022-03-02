from discord.ext import commands

class DontLoadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        assert "Shouldn't have been loaded."

def setup(bot: commands.Bot):
    bot.add_cog(DontLoadCog(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog("DontLoadCog")