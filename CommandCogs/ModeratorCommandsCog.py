import discord, os, asyncio
from discord.ext import commands
from discord.utils import get
import typing as t

from data.configurations import is_moderator, serverInfo

class ModeratorCommandsCog(commands.Cog, name="Moderator Commands"):
    """Special commands for moderators."""
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await is_moderator(ctx)

    def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        print("Error in ModeratorCommandsCog:", type(error), error)

    @commands.group(name="moderators", description="Everything about moderators.", pass_context=True, invoke_without_command=True, aliases=["mods"])
    async def moderators(self, ctx: commands.Context):
        """Used to determine the moderator roles for the server. Also all roles that has the `manage guild` permission are considered moderator as default."""
        ids = await serverInfo.get_mod_roles(ctx.guild.id)
        result = "There are " + str(len(ids)) + " moderator roles.\n\n"
        for i in range(len(ids)):
            result += get(ctx.guild.roles, id=ids[i]).name + "\n"
        await ctx.send(result)

    @moderators.command(name="add", description="Adds a moderator role to bot for this guild.", pass_context=True)
    async def add_moderator(self, ctx, role: discord.Role):
        """Adds a moderator role for this guild."""
        await serverInfo.set_mod_role(ctx.guild.id, role.id)
        await ctx.send("Done.")
        
    @moderators.command(name="remove", description="Removes a moderator role from bot.", pass_context=True)
    async def remove_moderator(self, ctx, role: discord.Role):
        """Removes a moderator role from bot."""
        await serverInfo.clear_mod_role(ctx.guild.id, role.id)
        await ctx.send("Done.")

    
    @commands.group(name="prefix", description="Changes the bots prefix.", pass_context=True, invoke_without_command=True)
    async def prefix(self, ctx, *args):
        """Prefix info for guild."""
        await ctx.trigger_typing()
        await ctx.send("My prefix for this server is " + str(await serverInfo.get_prefix(ctx.guild.id)) + ".", reference=ctx.message)

    @prefix.command(name="set", description="Sets a new prefix.", pass_context=True)
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        """Changes the bot's prefix."""
        await ctx.trigger_typing()

        await serverInfo.set_prefix(ctx.guild.id, new_prefix)
        await ctx.send("New prefix is: " + new_prefix)