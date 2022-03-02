from data import Table
from data.database import Column
from data.query import DeleteQuery, SelectQuery, SetQuery


firstLevelPoint = 5
pointMult = 2

class PointSystem:
    def __init__(self):
        columns = [
            Column("guildId", "integer", "not null"),
            Column("userId", "integer", "not null"),
            Column("points", "integer", 'default "0"'),
        ]
        self._pointDB = Table("points_data", ["guildId", "userId"], columns=columns)

        self._pointNameDB = Table("point_names", ["guildID"], columns=[Column("point_name", "TEXT", ["NOT NULL"])])
        
    def ConvertPointToLevel(self, points):
        level = 0
        currentLevelStartPoint = firstLevelPoint
        while (True):
            if (points - currentLevelStartPoint < 0):
                break

            currentLevelStartPoint *= pointMult
            level += 1

        currentLevelPoint = currentLevelStartPoint/2
        nextLevelPoint = currentLevelStartPoint
        percent = (points - currentLevelPoint) * 100 / (nextLevelPoint - currentLevelPoint)

        return (level, points, percent)

    async def GetPointName(self, serverId):
        query = SelectQuery(columns=["point_name"]).add_where(equals={"guildID": serverId})
        result = await self._pointNameDB.get(query)
        return result[0] if result else "Points"

    async def SetPointName(self, serverId, newName):
        query = SetQuery(setDict={"guildId":serverId, "point_name": newName})
        return await self._pointNameDB.set(query)

    async def GetPoints(self, serverId, userId):
        query = SelectQuery(columns=["points"]).add_where(equals={"guildID": serverId, "userId": userId})
        result = await self._pointDB.get(query)
        return result[0]["points"] if result else 0
        
    async def GetLevelInfo(self, serverId, userId):
        points = await self.GetPoints(serverId, userId)
        return self.ConvertPointToLevel(points)

    async def SetPoints(self, serverId, userId, points):
        query = SetQuery(setDict={"guildId":serverId, "userId": userId, "points": points})
        return await self._pointDB.set([serverId,userId], query)

    async def AddPoints(self, serverId, userId, points):
        curr_points = await self.GetPoints(serverId, userId)
        await self.SetPoints(serverId, userId, curr_points + points)

    async def GetInfoString(self, member):
        infoStr = await pointDb.GetLevelInfo(member.guild.id, member.id)
        level = infoStr[0]
        points = infoStr[1]
        percent = infoStr[2]
        point_name = await self.GetPointName(member.guild.id)
        
        infoString = member.mention + f"'s {(point_name + ' ') if point_name != '' else ''}level is " + str(level) + ", their current level is " + str(int(percent)) + "% done. (" + str(points) + ")\n"
        return infoString


    async def ResetServerLevels(self, serverId):
        query = DeleteQuery().add_where(equals={"guildId":serverId})
        await self._pointDB.delete_row(query)

pointDb = PointSystem()