import discord
from discord.ext import commands
import asyncio

from discord.ext.commands.errors import ExtensionNotFound, ExtensionNotLoaded

import Extensions

class OwnerCommandsCog(commands.Cog, name="Owner Commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        return self.bot.is_owner(ctx.author)

    @commands.command(name="shutdown", description="Shuts the bot down.", pass_context=True)
    async def shutdown(self, ctx: commands.Context):
        """Starts the alarms and the countdown."""
        await ctx.send("I'm going off, see ya.")

        await asyncio.sleep(3)
        await self.bot.close()

    @commands.group(name="extensions", description="All operations about extensions.\nExtension name may be needed to work for some commands.", pass_context=True, aliases=["extension"], invoke_without_command=True)
    async def extensions(self, ctx: commands.Context, *args):
        if (len(args) == 0):
            loaded_extensions = Extensions.get_pure_extension_list(self.bot)
            not_loaded_extensions = []
            for extension in Extensions.get_all_extension_list():
                if (not extension in loaded_extensions):
                    not_loaded_extensions.append(extension)

            embed = discord.Embed(title="Extensions", description="Currently loaded extensions are listed below.", color=discord.Color.green())
            loaded_string = "\n".join(loaded_extensions)
            if (loaded_string == ""):
                loaded_string = "There is no loaded extension."
            embed.add_field(name="Loaded Extensions", value=loaded_string)

            not_loaded_string = "\n".join(not_loaded_extensions)
            if (not_loaded_string == ""):
                not_loaded_string = "All extensions are loaded."
            embed.add_field(name="Unloaded Extensions", value=not_loaded_string)

            await ctx.send(embed=embed, reference=ctx.message)
            
        elif (len(args) > 0):
            await ctx.send(f"Couldn't get what you meant. Type '{ctx.prefix}help extensions' to get help.")

    @extensions.error
    async def extensions_command_error(self, ctx: commands.Context, exc: discord.DiscordException):
        print("Exception in extensions command:", exc, exc.args, sep="\n")


    @extensions.command(name="load", pass_context=True)
    async def extensions_load(self, ctx: commands.Context, *args):
        loaded_extensions = Extensions.get_pure_extension_list(self.bot)
        not_loaded_extensions = []
        for extension in Extensions.get_all_extension_list():
            if (not extension in loaded_extensions):
                not_loaded_extensions.append(extension)

        to_load = " ".join(args)
        if (to_load in not_loaded_extensions):
            Extensions.load_extension(self.bot, to_load)
            await ctx.send("Extension loaded.")
        else:
            await ctx.send("Extension couldn't be loaded.")

            
    @extensions.command(name="unload", pass_context=True)
    async def extensions_unload(self, ctx: commands.Context, *args):
        loaded_extensions = Extensions.get_pure_extension_list(self.bot)
        not_loaded_extensions = []
        for extension in Extensions.get_all_extension_list():
            if (not extension in loaded_extensions):
                not_loaded_extensions.append(extension)

        to_unload = " ".join(args)
        if (to_unload in loaded_extensions):
            Extensions.unload_extension(self.bot, to_unload)
            await ctx.send("Extension unloaded.")
        else:
            await ctx.send("Extension couldn't be unloaded.")
            
    @extensions.command(name="reload", pass_context=True)
    async def extensions_reload(self, ctx: commands.Context, *args):
        try:
            Extensions.reload_extension(self.bot, " ".join(args))
            await ctx.send("Reloaded extension.")
        except (ExtensionNotFound, ExtensionNotLoaded):
            await ctx.send("Couldn't reload extension.")
            
    @extensions.command(name="reload_all", pass_context=True)
    async def extensions_reload_all(self, ctx: commands.Context, *args):
        loaded_extensions = Extensions.get_pure_extension_list(self.bot)
        not_loaded_extensions = []
        for extension in Extensions.get_all_extension_list():
            if (not extension in loaded_extensions):
                not_loaded_extensions.append(extension)

        for extensionName in loaded_extensions:
            Extensions.reload_extension(self.bot, extensionName)

        await ctx.send("Reloaded all loaded extensions.")

    @extensions.command(name="load_all", pass_context=True)
    async def extensions_load_all(self, ctx: commands.Context, *args):
        Extensions.unload_loaded_extensions(ctx.bot)
        Extensions.load_all_extensions(ctx.bot)
        await ctx.send("Loaded all extensions.")