import discord
from discord.ext import commands
import typing as t

from data.configurations import is_moderator
from .PointDB import pointDb

class LevelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category_name = "Commands"


    @commands.command(name="level", description="To learn how much points you have.", pass_context=True, guild_only = True, aliases=["point", "points"])
    async def ask_point(self, ctx: commands.Context):
        """To learn how much points you have."""
        serverId = ctx.guild.id
        lookForUser = ctx.author

        lookForUsers = []
        mentions = ctx.message.mentions
        if (len(mentions) > 0):
            lookForUsers.extend(mentions)

        channel_mentions = ctx.message.channel_mentions
        if (len(channel_mentions) > 0):
            for channel in channel_mentions:
                lookForUsers.extend(channel.members)

        role_mentions = ctx.message.role_mentions
        if (len(role_mentions) > 0):
            for role in role_mentions:
                lookForUsers.extend(role.members)

        if (len(lookForUsers) == 0):
            lookForUsers.append(lookForUser)
        
        titleString = ""
        infoString = ""
        if (len(lookForUsers) > 1):
            point_name = await pointDb.GetPointName(serverId)
            if (point_name != ""):
                titleString += f"{point_name}\n"
            else:
                titleString += "Points\n"
                
        for user in lookForUsers:
            if ((await pointDb.GetPoints(serverId, user.id)) > 0):
                infoString += await pointDb.GetInfoString(user)

        embed = discord.Embed(title=titleString, description=infoString, color=discord.Color.green())
        await ctx.send(reference=ctx.message, embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.guild != None):
            await pointDb.AddPoints(message.guild.id, message.author.id, 1)
            
    @commands.Cog.listener()
    async def on_reaction_add(bot, reaction: discord.Reaction, user):
        if(reaction.message.guild != None):
            await pointDb.AddPoints(reaction.message.guild.id, user.id, 1)



class LevelsModeratorCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category_name = "Moderator Commands"

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await is_moderator(ctx)
        
    @commands.command(name="reset_points", description="Resets all points in server.")
    async def reset_server_level(self, ctx: commands.Context):
        """Resets all points for this server."""
        await pointDb.ResetServerLevels(ctx.guild.id)
        await ctx.send("Done.")
        
    @commands.command(name="set_pointname", description="Sets the name of the points in server.")
    async def set_point_name(self, ctx: commands.Context, arg: t.Optional[str]):
        if (arg):
            await pointDb.SetPointName(ctx.guild.id, arg)
            await ctx.send(f"Set the point name to '{arg}'.", reference=ctx.message)
        else:
            await ctx.send(f"Current point name is '{await pointDb.GetPointName(ctx.guild.id)}'.", reference=ctx.message)

def setup(bot: commands.Bot):
    bot.add_cog(LevelsCog(bot))
    bot.add_cog(LevelsModeratorCommands(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog("LevelsCog")
    bot.remove_cog("LevelsModeratorCommands")