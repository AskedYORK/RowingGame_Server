# -*- coding: utf-8 -*-
# import KBEngine
import KBEngine
from KBEDebug import *


class Room(KBEngine.Entity):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        self.createCellEntityInNewSpace(None)
        self.roomKey = self.cellData["roomKey"]
        self.RoomType = self.cellData["RoomType"]
        self.MaxPlayerCount = self.cellData["MaxPlayerCount"]

    def NeedPlayersCount(self):
        if self.isDestroyed:
            return 0
        print(str(self.roomKey) + "-需要玩家数量--" + str(self.MaxPlayerCount - len(self.EnterPlayerList)))
        return self.MaxPlayerCount - len(self.EnterPlayerList)

    def enterRoom(self, entityCall):
        if entityCall not in self.EnterPlayerList:
            self.EnterPlayerList.append(entityCall)

        if len(self.EnterPlayerList) == self.MaxPlayerCount and self.RoomType == 0:
            KBEngine.globalData["Halls"].roomIsFull(self, self.roomKey)

        if self.cell is not None:
            # 向cell投送玩家
            if self.cell is not None:
                self.cell.enterRoom(entityCall)

    def leaveRoom(self, entityId):
        for i in range(len(self.EnterPlayerList)):
            if self.EnterPlayerList[i] == entityId:
                self.EnterPlayerList.pop(i)
                break
        if self.RoomType == 0:
            KBEngine.globalData["Halls"].roomNeedPlayer(self, self.roomKey)


    def onGetCell(self):
        '''
        KBEngine method.
        entity的cell部分实体被创建成功
        :return:
        '''

        for playerEntity in self.EnterPlayerList:
            self.enterRoom(playerEntity)

        if self.MaxPlayerCount > len(self.EnterPlayerList) and self.RoomType == 0:
            KBEngine.globalData["Halls"].roomNeedPlayer(self, self.roomKey)

    def CanEnterRoom(self, entityCall):
        if entityCall.cell is None:
            print("room has no cell")
            entityCall.createCell(self.cell)
        else:
            entityCall.OnTeleport(self)

    def changeRoomSuccess(self, playerEntity):
        for i in range(len(self.EnterPlayerList)):
            if self.EnterPlayerList[i] == playerEntity:
                self.EnterPlayerList.pop(i)
                if self.RoomType == 0:
                    KBEngine.globalData["Halls"].roomNeedPlayer(self, self.roomKey)
                self.cell.changeRoomSuccess(playerEntity.id)
                break
