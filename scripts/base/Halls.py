# -*- coding: utf-8 -*-
# import KBEngine
import KBEngine
from KBEDebug import *
import random
import Functor

ALLOC_TIMER = 1
ROOM_MAX_PLAYER = 5


class Halls(KBEngine.Entity):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        KBEngine.globalData["Halls"] = self
        self.matchAllocTimer = 0
        self.waitingEnterPlayerEntities = []
        self.needPlayerRoomEntity = {}
        self.allRoomEntityList = {}

    def EnterMatchesMatch(self, entityCall):
        if entityCall in self.waitingEnterPlayerEntities:
            print("已经在匹配队列中了。。。。")
            return
        print("---------------bu zai pi pei dui lie ")
        self.waitingEnterPlayerEntities.append(entityCall)
        if self.matchAllocTimer == 0:
            self.matchAllocTimer = self.addTimer(0, 0.1, ALLOC_TIMER)

    def onTimer(self, timerHandle, userData):
        if userData == ALLOC_TIMER:
            self.allocRoom()

    def allocRoom(self):
        print("alloc room 0")
        if len(self.waitingEnterPlayerEntities) == 0 and self.matchAllocTimer != 0:
            self.delTimer(self.matchAllocTimer)
            self.matchAllocTimer = 0
            return

        print("alloc room 1")
        # 处理玩家加入房间逻辑
        playerCount = len(self.waitingEnterPlayerEntities)
        print("wait join room playerCount:", playerCount)
        if playerCount > 0:
            deleRoomList = []
            for roomId, entity in self.needPlayerRoomEntity.items():
                freeSeat = entity.NeedPlayersCount()
                if freeSeat > 0:
                    if playerCount < freeSeat:
                        for i in range(playerCount):
                            entity.enterRoom(self.waitingEnterPlayerEntities.pop(0))
                            playerCount -= 1
                    else:
                        for i in range(freeSeat):
                            entity.enterRoom(self.waitingEnterPlayerEntities.pop(0))
                            playerCount -= 1
                        deleRoomList.append(roomId)

                    if playerCount == 0:
                        return

            for i in range(len(deleRoomList)):
                self.needPlayerRoomEntity.pop(deleRoomList[i])

            if playerCount > 0:
                # 房间检查了一遍发现还是没有玩家分配完，就创建一个新房间
                if playerCount > ROOM_MAX_PLAYER:
                    for i in range(playerCount % ROOM_MAX_PLAYER):
                        self._createRoom(ROOM_MAX_PLAYER)
                        playerCount -= ROOM_MAX_PLAYER
                if playerCount > 0:
                    self._createRoom(playerCount)
                    playerCount -= playerCount

    def _createRoom(self, playerCount):
        print("_createRoom----playerCount:", playerCount)
        EntityList = []
        for i in range(playerCount):
            EntityList.append(self.waitingEnterPlayerEntities.pop(0))
        self._createRoomEntity(EntityList)

    def _createRoomEntity(self, entityList, roomType=0):
        roomId = self.generateRoomId()
        print("_createRoomEntity roomId:", roomId)
        if self.allRoomEntityList.get(roomId, None) is not None:
            self._createRoomEntity(entityList, roomType)

        props = {
            "roomKey": roomId,
            "RoomType": roomType,
            "EnterPlayerList": entityList,
            "MaxPlayerCount": ROOM_MAX_PLAYER
        }
        print("_createRoomEntity props:")
        KBEngine.createEntityAnywhere("Room", props, Functor.Functor(self._createRoomCB, roomId))

    def _createRoomCB(self, roomId, entityCall):
        print("_createRoomCB---roomId:", roomId, "--entityCall:", entityCall.id)
        self.allRoomEntityList[roomId] = entityCall

    def generateRoomId(self):
        roomid = ""
        roomId_1 = random.randint(1, 9)
        roomid = str(roomId_1)
        for num in range(0, 5):
            roomId_n = random.randint(0, 9)
            roomid = roomid + str(roomId_n)
        return int(roomid)

    def roomNeedPlayer(self, entityCall, roomId):
        '''
        房间通知大厅，需要玩家来填满
        :param entityCall:
        :return:
        '''
        self.needPlayerRoomEntity[roomId] = entityCall

    def roomIsFull(self, entityCall, roomId):
        if self.needPlayerRoomEntity.get(roomId, None) is not None:
            self.needPlayerRoomEntity.pop(roomId)

    def changeRoom(self, entityMailBox, curRoomId):
        isEnterNewRoom = False
        if len(self.needPlayerRoomEntity) > 0:
            for roomId in list(self.needPlayerRoomEntity):
                if roomId != curRoomId:
                    self.needPlayerRoomEntity[roomId].enterRoom(entityMailBox)
                    isEnterNewRoom = True

        if isEnterNewRoom == False:
            EntityList = [entityMailBox]
            self._createRoomEntity(EntityList)
            isEnterNewRoom = True

        if isEnterNewRoom:
            # 切换房间成功，清除上一个房间交换者的数据
            self.allRoomEntityList[curRoomId].changeRoomSuccess(entityMailBox)
        else:
            print("changeRoom has no more room")
