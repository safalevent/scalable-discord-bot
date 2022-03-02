import Extensions
import discord
import Constants
from discord.ext import commands
from discord.flags import Intents

from data.configurations import serverInfo

from CommandCogs.CommandsCog import CommandsCog
from CommandCogs.ModeratorCommandsCog import ModeratorCommandsCog
from CommandCogs.OwnerCommandsCog import OwnerCommandsCog

import logging

logging.basicConfig(level=logging.INFO)

async def get_prefix(client, message=None):
    if (message and message.guild):
        return await serverInfo.get_prefix(message.guild.id)
    else:
        return Constants.default_prefix

commandPrefix = get_prefix

intents = Intents.default() 
intents.reactions = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix=commandPrefix, description=Constants.description, intents=intents, owner_ids=set(Constants.bot_owners), help_command=None)

@bot.event
async def on_ready():
    logging.info("Logged on as  {0}!".format(bot.user))

@bot.event
async def on_message(message: discord.Message):
    if (message.author == bot.user):
        return

    lowerContent = message.content.lower()
    if (bot.user in message.mentions and "help" in lowerContent):
        await message.channel.send("You can type " + serverInfo.get_prefix(message.guild.id) + "help to get more information.", reference=message)

    await bot.process_commands(message)

bot.add_cog(CommandsCog(bot))
bot.add_cog(ModeratorCommandsCog(bot))
bot.add_cog(OwnerCommandsCog(bot))

Extensions.load_all_extensions(bot)

with open("./token", "r", encoding="utf-8") as tf:
    bot.run(tf.read())