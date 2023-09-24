import discord
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.partial_emoji import PartialEmoji
import typing as t
from typing import Optional

from requests import delete

from .enums import Result

class _ChooseFromSelect(discord.ui.Select):
    async def callback(self, interaction: discord.Interaction):
        self.view.chosenIndex = int(self.values[0])
        await interaction.response.defer()
        self.view.stop()

class _ChooseWithButton(discord.ui.Button):
    def __init__(self, index, *, style: ButtonStyle = ..., label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[t.Union[str, Emoji, PartialEmoji]] = None, row: Optional[int] = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.callbackValue = index

    async def callback(self, interaction: discord.Interaction):
        self.view.chooser = interaction.user
        self.view.chosenIndex = self.callbackValue

        if (self.callbackValue >= 0):
            self.view.result = Result.COMPLETED
        else:
            self.view.result = Result.CANCEL

        self.view.stop()

class _SurveyButton(discord.ui.Button):
    def __init__(self, name, *, style: ButtonStyle = ..., disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[t.Union[str, Emoji, PartialEmoji]] = None, row: Optional[int] = None):
        super().__init__(style=style, label=name + " (0)", disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        
        self.name = name
        self.vote_count = 0
        self.votes = set()

    async def callback(self, interaction: discord.Interaction):
        if (await self.view.CanVote(interaction.user)):
            await self.view.CheckVote(interaction.user)
            await self.AddVote(interaction.user)
            await self.view.UpdateMessage()

        await interaction.response.defer()

    async def AddVote(self, user: discord.User):
        if user not in self.votes:
            self.vote_count += 1
            self.votes.add(user)
            await self.UpdateButton()

    async def DeleteVote(self, user: discord.User):
        if user in self.votes:
            self.votes.remove(user)
            self.vote_count -= 1
            await self.UpdateButton()

    async def UpdateButton(self):
        self.label = self.name + " (" + str(self.vote_count) + ")"
        
class _GetFirstClickButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ..., label: t.Optional[str] = None, disabled: bool = False, custom_id: t.Optional[str] = None, url: t.Optional[str] = None, emoji: t.Optional[t.Union[str, Emoji, PartialEmoji]] = None, row: t.Optional[int] = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_user = interaction.user
        if (self.view.message):
            await self.view.message.edit(view=None)
        self.view.stop()