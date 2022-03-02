import discord
from discord.ext import commands
import typing as t

from .database import Table, Column
from .query import DeleteQuery, SelectQuery, SetQuery

async def is_moderator(ctxoruser: t.Union[commands.Context, discord.Member]):
    user = ctxoruser
    if isinstance(ctxoruser, commands.Context):
        user = ctxoruser.author

    if user:
        result = False
        if (user.guild):
            result = await serverInfo.check_mod_role(user.guild.id, user.top_role.id)

        if not result:
            result = user.guild_permissions.manage_guild

        return result

    return False

class ServerInfo:
    def __init__(self):
        columns = [Column("Prefix", "integer", ['DEFAULT "!"'])]
        self.prefix_data = Table("Guild_Prefix_Info", "guildID", columns=columns)

        mods_columns = [
            Column("guildID", "integer", ['NOT NULL']),
            Column("roleID", "integer", ['NOT NULL'])
            ]
        self.mods_data = Table("Guild_Mods_Info", ["guildID", "roleID"], columns=mods_columns)
    
    async def get_prefix(self, guildId):
        guild_row = await self.prefix_data.get_with(guildId, SelectQuery(columns="Prefix"))
        if not guild_row:
            await self.prefix_data.set(guildId)
            guild_row = await self.prefix_data.get_with(guildId, SelectQuery(columns="Prefix"))
        
        prefix = guild_row[0]
        return prefix

    async def set_prefix(self, guildId, newPrefix: str):
        setQuery = SetQuery(setDict={"Prefix": newPrefix})
        return await self.prefix_data.set(guildId, setQuery)


    async def get_mod_roles(self, guildId):
        guild_roles = await self.mods_data.get(SelectQuery(columns="roleID").add_where(equals={"guildID": guildId}))
        return [row[0] for row in guild_roles]

    async def check_mod_role(self, guildId, roleId):
        guild_roles = await self.mods_data.get(SelectQuery(columns="roleID").add_where(equals={"guildID": guildId, "roleID": roleId}))
        return len(guild_roles) > 0

    async def set_mod_role(self, guildId, roleId):
        setQuery = SetQuery(setDict={"guildID": guildId, "roleID": roleId})
        return await self.mods_data.set(setQuery)
    
    async def clear_mod_role(self, guildId, roleId):
        setQuery = DeleteQuery().add_where(equals={"guildID": guildId, "roleID": roleId})
        return await self.mods_data.delete_row(setQuery)


serverInfo = ServerInfo()