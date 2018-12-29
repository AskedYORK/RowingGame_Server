# -*- coding: utf-8 -*-
# import KBEngine
import KBEngine
from KBEDebug import *


class Room(KBEngine.Entity):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        KBEngine.addSpaceGeometryMapping(self.spaceID, None, "spaces/rowingGameRoom")
        KBEngine.globalData["Room_%i" % self.spaceID] = self
        self.roomInfo = roomInfo(self.roomKey, self.MaxPlayerCount)
        self.gameState = None

    def enterRoom(self, entityCall):
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.userId  == 0:
                seat.userId = entityCall.id
                seat.score = 1000
                self.base.CanEnterRoom(entityCall)
                entityCall.enterRoomSuccess(self.roomKey)
                return

    def ReqLeaveRoom(self, entityCall):
        # 通知玩家base销毁cell
        entityCall.base.onLeaveRoom()
        # 让base向大厅要人
        self.base.leaveRoom(entityCall.id)
        # 清除该玩家的实体数据
        self.roomInfo.clearDataByEntityId(entityCall.id)

    def changeRoomSuccess(self, entityId):
        self.roomInfo.clearDataByEntityId(entityId)

    #
    # def reqChangeReadyState(self, entityCall, isReady):
    #     pass


#----------------------------------------------------------------------
class gameState:
    def __init__(self):
        self.state = "idle"

class roomInfo:
    def __init__(self, roomKey, maxPlayerCount):
        self.id = roomKey
        self.seats = []

        for i in range(maxPlayerCount):
            seat = seat_roomInfo(i)
            self.seats.append(seat)

    def claerData(self):
        for i in range(len(self.seats)):
            self.clearDataBySeat(i, False)


    def clearDataBySeat(self, index, isOut = True):
        s = self.seats[index]
        if isOut:
            s.userId = 0
        s.ready = 0
        s.score = 0
        s.position = {}
        s.direction = {}
        s.seatIndex = index

    def clearDataByEntityId(self, entityId, isOut = True):
        for i in range(len(self.seats)):
            if self.seats[i].userId == entityId:
                self.clearDataBySeat(i, isOut)
                break



class seat_roomInfo:
    def __init__(self, seatIndex):
        self.userId = 0
        self.score = 0
        self.position = {}
        self.direction = {}
        self.ready = False
        self.seatIndex = seatIndex


