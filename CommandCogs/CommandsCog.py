from random import uniform, choice, randint
import discord
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands.core import Group
import typing as t

from data.configurations import serverInfo

class CommandsCog(commands.Cog, name="Commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    # Ref: https://stackoverflow.com/a/65089774/14145833
    @commands.hybrid_command()
    async def help(self, ctx: commands.Context, args=None):
        """Helps."""
        help_embed = discord.Embed(description="", colour=Color.blurple())
        command_names_list = [x.name for x in self.bot.commands]

        # If there are no arguments, just list the commands:
        if not args:
            help_embed.description += self.bot.description

            categoryDict = {}
            for cogName in self.bot.cogs:
                cog = self.bot.cogs[cogName]
                
                if(hasattr(cog, "category_name")):
                    key = cog.category_name
                else:
                    key = cogName

                if (len(cog.get_commands()) == 0):
                    continue
                
                commands = []
                for command in cog.get_commands():
                    if (await command.can_run(ctx)):
                        commands.append(command)

                if (len(commands) > 0):
                    if (not key in categoryDict):
                        categoryDict[key] = []

                    categoryDict[key].extend(commands)
            
            for category, commands in categoryDict.items():
                help_embed.add_field(
                    name=category,
                    value=" ".join([x.name for x in commands]),
                    inline=False
                )

            help_embed.add_field(
                name="Details",
                value=f"Type `{ctx.prefix if ctx.prefix else await serverInfo.get_prefix(ctx.guild.id)}help [command]` for more details about each command.",
                inline=False
            )

        # If the argument is a command, get the help text from that command:
        elif args in command_names_list and await (command := self.bot.get_command(args)).can_run(ctx):
            cog = command.cog

            group = None
            if (cog != None):
                for command in cog.walk_commands():
                    if command.qualified_name == args:
                        if (isinstance(command, Group)):
                            group = command
                        break

            if (group != None):
            
                help_embed.title = command.qualified_name
                help_embed.description = command.help

                for subcommand in sorted(group.commands, key=lambda x: x.qualified_name):
                    try:
                        can_run = await subcommand.can_run(ctx)
                    except:
                        can_run = False
                        
                    if (can_run):
                        name = subcommand.qualified_name
                        
                        if (subcommand.aliases):
                            name += f"\t`{'` `'.join(subcommand.aliases)}`"

                        value = subcommand.help or ""

                        if (subcommand.usage):
                            value += f"\n`Usage: {subcommand.usage}`"

                        value = value.strip()
                        if (value == ""):
                            value = "No extra info."

                        help_embed.add_field(
                            name=name,
                            value=value,
                            inline=False
                        )
            
            else:
                help_embed.add_field(
                    name=args,
                    value=command.help,
                    inline=False
                )

            if (command.usage != None):
                help_embed.add_field(
                    name="Usage Format",
                    value=command.usage
                )


            if(len(command.aliases) > 0):
                help_embed.add_field(
                    name="Command Aliases",
                    value=" ".join(command.aliases),
                    inline=True
                )

        # If someone is just trolling:
        else:
            help_embed.add_field(
                name="Nope.",
                value="I don't think that command exists."
            )

        await ctx.send(embed=help_embed)

    @commands.hybrid_command(name="random", description="Makes a random choice between the given numbers or the people in the channel.", aliases=["seç", "rastgele", "r"])
    @discord.app_commands.describe(
        numbers="Optinal, makes the bot work as a RNG."
    )
    async def random(self, ctx: commands.Context, *, numbers: t.Optional[str] = None):
        """Makes a random choice of people or numbers."""
        numbers = numbers.strip().split()
        if(len(numbers) >= 2):
            try:
                has_float = False
                dots = [",", "."]
                if (any(x in numbers[0] for x in dots)):
                    first = float(numbers[0])
                    has_float = True
                else:
                    first = int(numbers[0])
                    
                if (any(x in numbers[1] for x in dots)):
                    second = float(numbers[1])
                    has_float = True
                else:
                    second = int(numbers[1])

                if (has_float):
                    num = round(uniform(first,second), 2)
                else:
                    num = randint(first, second)
                    
                await ctx.send("I choose " + str(num) + ".", reference=ctx.message)
                return

            except (ValueError):
                pass

        members = ctx.channel.members

        await ctx.send("I choose you, " + choice(members).mention + ".", reference=ctx.message)