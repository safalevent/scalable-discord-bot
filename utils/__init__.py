from datetime import datetime
import re
import discord
from discord.abc import User
from discord.errors import InvalidArgument
from discord.ext.commands.bot import Bot
from discord.interactions import Interaction
from discord.message import Message
from discord.utils import utcnow
import typing as t
import pytz

from .errors import NoOption
from .ui import *

async def ask_to_select(channelOrInteract: t.Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel, Interaction], choosers: t.List[discord.User], options: t.List[t.Any], *, question="Which one do you select?", ephemeral=True, show_chosen=False, delete_after=False):
    """
    An async function to get user select an option from the given options.

    Raises:
    NoOption when there is no option.
    TimeoutError when select timeouts.
    """
    if not options:
        raise NoOption("ask_to_select function needs options to select.")

    if not isinstance(choosers, list):
        choosers = [choosers]

    view = ChooseFromView(options, choosers=choosers)

    if isinstance(channelOrInteract, Interaction):
        await channelOrInteract.response.send_message(content=question, view=view, ephemeral=ephemeral)
    else:
        message = await channelOrInteract.send(content=question, view=view)
    
    selectOptions = options
    page = 0
    moreThan25 = len(options) > 25
    selected = None
    while not selected:
        if moreThan25:
            selectOptions = options[(0 + (page * 24)):(24 + (page * 24))]
            selectOptions.append("Show more...")

        timed_out = await view.wait()
        if not timed_out:
            selectedIndex = int(view.chosen)
            if not (moreThan25 and selectedIndex == len(selectOptions) - 1):
                selected = selectOptions[selectedIndex]

        else:
            for item in view.children:
                item.disabled = True

            if isinstance(channelOrInteract, Interaction):
                await channelOrInteract.edit_original_message(content="Options timed out.", view=view)
            else:
                await message.edit(content="Options timed out.", view=view)

            raise TimeoutError()
            
    if isinstance(channelOrInteract, Interaction):
        if delete_after:
            pass
            # await channelOrInteract.delete_original_message() # Can't delete ephemerals.
        elif show_chosen:
            await channelOrInteract.edit_original_message(content=f"You have selected '{selected}'.", view=None)
    else:
        if delete_after:
            await message.delete()
        elif show_chosen:
            await message.edit(content=f"'{selected}' has been selected.", view=None)
        else:
            for ch in view.children:
                ch.disabled = True

            await message.edit(view=view)

    return selected


async def get_date(date_args: str):
    """Creates an date object using the format dd.mm.yyyy, HH:MM and Zone Name."""
    date = datetime.now()
    if isinstance(date_args, str):
        date_args = date_args.split()

    timezoneArgsDict = {"CET": "Europe/Berlin"}
    
    for arg in date_args:
        dotSplit = arg.split(".")
        if len(dotSplit) == 3:
            day, month, year = map(int, dotSplit)
            date = date.replace(day=day, month=month, year=year, hour=0, minute=0, second=0)
            continue

        elif len(dotSplit) > 1:
            raise InvalidArgument()
        
        colonSplit = arg.split(":")
        if len(colonSplit) == 2:
            hour, minute = map(int, colonSplit)
            date = date.replace(hour=hour, minute=minute, second=0)
            continue
        
        elif len(colonSplit) > 1:
            raise InvalidArgument()

        try:
            if (arg in timezoneArgsDict):
                arg = timezoneArgsDict[arg]

            tmz = pytz.timezone(arg)
            date = tmz.localize(date)
            continue
        except pytz.UnknownTimeZoneError:
            pass
    
    if (not date.tzinfo):
        date = pytz.timezone("Europe/Istanbul").localize(date)
    return date
    
async def get_response_from_dm(bot: Bot, user: User, question: str):
    """Gets user response from dm for the question.
    
    Assumes the channel is already claimed."""
    def check(m: Message):
        return m.author == user and m.channel == user.dm_channel

    sent = await user.send(question)
    message = await bot.wait_for("message", check = check)

    value = message.content
    await sent.delete()
    return value

async def check_if_url(link):
    return True
    if not isinstance(link, str):
        return False
    
    link = link.strip()
    pattern = re.compile("((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")
    regex = pattern.fullmatch(link)
    return regex != None