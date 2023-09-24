import discord
import logging, traceback
from discord.ext import commands
from discord.ext.commands.errors import CheckFailure, MissingRequiredArgument


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.logger = logging.getLogger(__name__.split(".")[-1])
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc: Exception):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        exc: Exception = getattr(exc, 'original', exc)

        if isinstance(exc, ignored):
            return

        if isinstance(exc, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(exc, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(exc, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')

        # elif isinstance(exc, CheckFailure):
        #     self.logger.error(f"Check failed on command: {ctx.command.qualified_name}")

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(str(exc).capitalize(), reference=ctx.message)

        else:
            errorStr = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            self.logger.error(f'Ignoring exception in command {ctx.command}:\n{errorStr}')

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))