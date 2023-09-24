import discord
from discord import ButtonStyle, Interaction, ui, Message
from discord.ext import commands
from discord.colour import Color
from discord.enums import ButtonStyle
from discord.utils import get
import typing as t


from .ui_internal import _GetFirstClickButton, _ChooseWithButton, _ChooseFromSelect, _SurveyButton
from .enums import Result

class ChooseFromView(discord.ui.View):
    def __init__(self, options: t.List[str], chooser=None, choosers=None, ignoreList=None, timeout=300, placeholder="Choose an option.", ignoreChoosers=False):
        super().__init__(timeout=timeout)

        if (choosers == None): choosers = []
        if (chooser != None): choosers.append(chooser)
        if (ignoreList == None): ignoreList = []

        if (ignoreChoosers):
            ignoreList.extend(choosers)

        self.chooserIds = [x.id for x in choosers]
        self.placeholder = placeholder
        self.ignoreList = ignoreList

        self.set_options(options=options)

        self.chosenIndex = None

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

        select = _ChooseFromSelect(placeholder=self.placeholder, options=given_options)
        self.add_item(select)


class ApproveDenyView(discord.ui.View):
    def __init__(self, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        self.approved = False

    @discord.ui.button(label="Approve", style=ButtonStyle.green)
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
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
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
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
    async def complete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.completed = True
        self.stop()
        
    @discord.ui.button(label="Remake", style=ButtonStyle.red)
    async def remake_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.completed = False
        self.stop()

class GetFirstClickView(discord.ui.View):
    def __init__(self, buttonLabel, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        self.message: discord.Message = None
        self.selected_user: discord.User = None

        self.add_item(_GetFirstClickButton(style=ButtonStyle.green, label=buttonLabel))

class CompleteRemakeCancelView(discord.ui.View):

    def __init__(self, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        self.result: Result = Result.UNKNOWN

    @discord.ui.button(label="Complete", style=ButtonStyle.green)
    async def complete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = Result.COMPLETED
        self.stop()
        
    @discord.ui.button(label="Remake", style=ButtonStyle.gray)
    async def remake_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = Result.REMAKE
        self.stop()
        
    @discord.ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = Result.CANCEL
        self.stop()

class SurveyWithButtonsView(discord.ui.View):
    def __init__(self, options: t.List[str], *, noVoteLabel: str = None, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        if noVoteLabel:
            self.add_item(_SurveyButton(name=noVoteLabel, style=ButtonStyle.red))

        self.result = Result.UNKNOWN
        for i, option in enumerate(options):
            self.add_item(_SurveyButton(name=option, style=ButtonStyle.green))

    async def CanVote(self, user: discord.User):
        return True

    async def CheckVote(self, user: discord.User):
        for child in self.children:
            await child.DeleteVote(user)

    async def UpdateMessage(self):
        if self.message:
            await self.message.edit(view=self)
            
    async def on_timeout(self) -> None:
        await super().on_timeout()
        for child in self.children:
            child.disabled = True

        if (self.message):
            await self.message.edit(view=self)


class ChooseWithButtonsView(discord.ui.View):
    def __init__(self, options: t.List[str], cancelButtonLabel: str = None, *, timeout: t.Optional[float] = 180):
        super().__init__(timeout=timeout)

        if cancelButtonLabel:
            self.add_item(_ChooseWithButton(index=None, style=ButtonStyle.red, label=cancelButtonLabel))

        self.chooser = None
        self.chosenIndex = None
        self.result = Result.UNKNOWN
        for i, option in enumerate(options):
            self.add_item(_ChooseWithButton(index=i, style=ButtonStyle.green, label=option))

class VotingView(ui.View):
    def __init__(self, needed_yes_count: int, *, timeout: t.Optional[float] = 180, yes_label="Yes", neutral_label="Neutral", no_label="No"):
        super().__init__(timeout=timeout)
        self.message: Message = None
        self.needed_yes = needed_yes_count
        self.yes_count = 0
        self.votes = {}

        self.yes_label = yes_label
        self.neutral_label = neutral_label
        self.no_label = no_label

        self.yes_won = False
        self.yes_button: discord.Button = get(self.children, label="Yes")
        self.yes_button.label = self.yes_label
        self.neutral_button: discord.Button = get(self.children, label="Neutral")
        self.neutral_button.label = self.neutral_label
        self.no_button: discord.Button = get(self.children, label="No")
        self.no_button.label = self.no_label

        self.count_button: discord.Button = get(self.children, label="Count")
        self.count_button.label = f"{self.yes_count}/{self.needed_yes}"

    async def on_timeout(self) -> None:
        await super().on_timeout()
        for child in self.children:
            child.disabled = True

        if (self.message):
            await self.message.edit(view=self)

    @ui.button(label="Yes", style=ButtonStyle.green)
    async def yes_button_impl(self, interaction: Interaction, button: ui.Button):
        if interaction.user in self.votes and self.votes[interaction.user] == 1:
            await interaction.response.defer()
            return
            
        self.yes_count += 1
        if interaction.user in self.votes:
            self.yes_count += 1

        self.votes[interaction.user] = 1

        await self.last_operations(button=button, interaction=interaction)
        
    @ui.button(label="Neutral", style=ButtonStyle.gray)
    async def neutral_button_impl(self, interaction: Interaction, button: ui.Button):
        if interaction.user in self.votes:
            self.yes_count -= self.votes[interaction.user]
            self.votes.pop(interaction.user)
            
        await self.last_operations(button=button, interaction=interaction)

    @ui.button(label="No", style=ButtonStyle.blurple)
    async def no_button_impl(self, interaction: Interaction, button: ui.Button):
        if interaction.user in self.votes and self.votes[interaction.user] == -1:
            await interaction.response.defer()
            return
            
        self.yes_count -= 1
        if interaction.user in self.votes:
            self.yes_count -= 1

        self.votes[interaction.user] = -1
    
        await self.last_operations(button=button, interaction=interaction)
        
    @ui.button(label="Count", style=ButtonStyle.gray, disabled=True)
    async def count_button_impl(self, interaction: Interaction, button: ui.Button):
        pass
        

    async def last_operations(self, button: ui.Button=None, interaction: Interaction=None):
        self.count_button.label = f"{self.yes_count}/{self.needed_yes}"
        
        ended = False
        if (self.yes_count >= self.needed_yes):
            ended = True
            for ch in self.children:
                ch.disabled = True

            self.yes_won = True

        if self.message:
            await self.message.edit(view=self)

        if ended:
            self.stop()

        await interaction.response.defer()