from enum import Enum
import discord
from discord.colour import Color
from discord.components import Button
from discord.emoji import Emoji
from discord.enums import ButtonStyle
import typing as t
from typing import Optional

from discord.partial_emoji import PartialEmoji

class ChooseFromSelect(discord.ui.Select):
    async def callback(self, interaction: discord.Interaction):
        self.view.chosen = self.values[0]
        self.view.stop()

class ChooseFromView(discord.ui.View):
    def __init__(self, options, chooser=None, choosers=None, ignoreList=None, timeout=300, placeholder="Choose an option."):
        super().__init__(timeout=timeout)

        if (choosers == None): choosers = []
        if (chooser != None): choosers.append(chooser)
        if (ignoreList == None): ignoreList = []

        self.chooserIds = [x.id for x in choosers]
        self.placeholder = placeholder
        self.ignoreList = ignoreList

        self.set_options(options=options)

        self.chosen = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id in self.chooserIds

    def set_options(self, options):
        self.clear_items()
        given_options = []
        for index, option in enumerate(options):
            if option in self.ignoreList:
                continue

            selectOption = discord.SelectOption(label=str(option), value=str(index))
            given_options.append(selectOption)

        select = ChooseFromSelect(placeholder=self.placeholder, options=given_options)
        self.add_item(select)


class ApproveDenyView(discord.ui.View):
    def __init__(self, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        self.approved = False

    @discord.ui.button(label="Approve", style=ButtonStyle.green)
    async def approve_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.approved = True

        embed = None
        if (interaction.message.embeds):
            embed = interaction.message.embeds[0]
            embed.color = Color.green()
            embed.insert_field_at(0, name="Status", value="Approved")

        if embed:
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.edit_message(content=(interaction.message.content + "\n\nApproved.").strip(), view=None)
        self.stop()
        
    @discord.ui.button(label="Deny", style=ButtonStyle.red)
    async def deny_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.approved = False

        embed = None
        if (interaction.message.embeds):
            embed = interaction.message.embeds[0]
            embed.color = Color.red()
            embed.insert_field_at(0, name="Status", value="Denied")

        if embed:
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.edit_message(content=(interaction.message.content + "\n\nDenied.").strip(), view=None)
        self.stop()


class CompleteRemakeView(discord.ui.View):
    def __init__(self, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        self.completed = False

    @discord.ui.button(label="Complete", style=ButtonStyle.green)
    async def complete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.completed = True
        self.stop()
        
    @discord.ui.button(label="Remake", style=ButtonStyle.red)
    async def remake_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.completed = False
        self.stop()

class _GetFirstClickButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ..., label: t.Optional[str] = None, disabled: bool = False, custom_id: t.Optional[str] = None, url: t.Optional[str] = None, emoji: t.Optional[t.Union[str, Emoji, PartialEmoji]] = None, row: t.Optional[int] = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_user = interaction.user
        if (self.view.message):
            await self.view.message.edit(view=None)
        self.view.stop()

class GetFirstClickView(discord.ui.View):
    def __init__(self, buttonLabel, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        self.message: discord.Message = None
        self.selected_user: discord.User = None

        self.add_item(_GetFirstClickButton(style=ButtonStyle.green, label=buttonLabel))

class Result(Enum):
    UNKNOWN = 0
    CANCEL = 1
    REMAKE = 2
    COMPLETED = 3

class CompleteRemakeCancelView(discord.ui.View):

    def __init__(self, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        self.result: Result = Result.UNKNOWN

    @discord.ui.button(label="Complete", style=ButtonStyle.green)
    async def complete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.result = Result.COMPLETED
        self.stop()
        
    @discord.ui.button(label="Remake", style=ButtonStyle.gray)
    async def remake_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.result = Result.REMAKE
        self.stop()
        
    @discord.ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.result = Result.CANCEL
        self.stop()

class _chooseWithButton(discord.ui.Button):
    def __init__(self, index, *, style: ButtonStyle = ..., label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[t.Union[str, Emoji, PartialEmoji]] = None, row: Optional[int] = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.callbackValue = index

    async def callback(self, interaction: discord.Interaction):
        self.view.chooser = interaction.user
        self.view.chosen = self.callbackValue

        if (self.callbackValue >= 0):
            self.view.result = Result.COMPLETED
        else:
            self.view.result = Result.CANCEL

        self.view.stop()


class ChooseWithButtonsView(discord.ui.View):
    def __init__(self, options: t.List[str], cancelButtonLabel: str = None, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        if cancelButtonLabel:
            self.add_item(_chooseWithButton(index=-1, style=ButtonStyle.red, label=cancelButtonLabel))

        self.chooser = None
        self.chosenIndex = -1
        self.result = Result.UNKNOWN
        for i, option in enumerate(options):
            self.add_item(_chooseWithButton(index=i, style=ButtonStyle.green, label=option))