# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

COUNT_DOWN_TIME = 5
COUNT_DOWN_TIME_GAME_END = 30

COUNT_DOWN_TIME_TAG = 10
COUNT_DOWN_TIME_END_TAG = 2


class Room(KBEngine.Entity):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        KBEngine.addSpaceGeometryMapping(self.spaceID, None, "spaces/rowingGameRoom")
        KBEngine.globalData["Room_%i" % self.spaceID] = self
        self.roomInfo = roomInfo(self.roomKey, self.MaxPlayerCount)
        self.gameState = None
        self.countDown = 0
        self.finishGameCount = 0
        self.endTime = COUNT_DOWN_TIME_GAME_END
        print("cell room init")

    def enterRoom(self, entityCall):
        print("enterRoom--id:", entityCall.id, "--len(self.roomInfo.seats):", len(self.roomInfo.seats))
        for i in range(len(self.roomInfo.seats)):
            print("enterRoom-----0")
            seat = self.roomInfo.seats[i]
            if seat.userId == 0:
                print("enterRoom-----1")
                seat.userId = entityCall.id
                seat.score = 1000
                seat.entity = entityCall
                entityCall.cell.playerReadyStateChange(seat.ready, seat.seatIndex)
                self.base.CanEnterRoom(entityCall)
                entityCall.enterRoomSuccess(self.roomKey)
                print("enterRoom-----2")
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

    def reqChangeReadyState(self, callerEntityID, STATE):
        print("cell room reqChangeReadyState---callerEntityID", callerEntityID, "--STATE:", STATE)
        # 设置座位上玩家的状态
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.userId == callerEntityID:
                seat.ready = not STATE
                seat.entity.cell.playerReadyStateChange(seat.ready, seat.seatIndex)
                print("reqChangeReadyState:", seat.ready, "--index:", seat.seatIndex)
                break

        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i];
            if not seat.ready:
                print("cell room has player not ready---", seat.userId, "---", seat.ready)
                return

        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            seat.entity.GameCountDown(COUNT_DOWN_TIME_TAG)
            print("inform all client GameCountDown")

        self.addTimer(0.1, 1, COUNT_DOWN_TIME_TAG)

    def PlayerFinishGame(self, entityId):
        print("PlayerFinishGame entityId:", entityId)
        self.finishGameCount += 1
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            seat.entity.PlayerFinishGame(entityId)
            print("PlayerFinishGame be formed player:", seat.entity.playerID)

        # 所有玩家完成比赛
        if self.finishGameCount == len(self.roomInfo.seats):
            self.endTime = 0

    def onTimer(self, id, userArg):
        # 游戏开始倒计时
        if COUNT_DOWN_TIME_TAG == userArg:
            if self.countDown < COUNT_DOWN_TIME:
                self.countDown += 1
                # 倒计时通知每一个玩家
                for i in range(len(self.roomInfo.seats)):
                    seat = self.roomInfo.seats[i]
                    seat.entity.GameCountDown(COUNT_DOWN_TIME - self.countDown)
                    print("inform all client GameCountDown")
            else:
                self.countDown = 0
                self.delTimer(id)
                self.addTimer(0, 1, COUNT_DOWN_TIME_END_TAG)
                self.IsGameStart = True
                # 倒计时完了，通知每一个玩家开始游戏
                for i in range(len(self.roomInfo.seats)):
                    seat = self.roomInfo.seats[i]
                    seat.entity.GameStart()

        elif COUNT_DOWN_TIME_END_TAG == userArg:
            if self.endTime > 0:
                self.endTime -= 1
                print("game over time count down", self.endTime)
            else:
                self.delTimer(id)
                self.endTime = COUNT_DOWN_TIME_GAME_END
                self.IsGameStart = False
                self.finishGameCount = 0
                # 倒计时完了，通知每一个玩家开始游戏
                print("game over")
                for i in range(len(self.roomInfo.seats)):
                    seat = self.roomInfo.seats[i]
                    seat.entity.GameOver()
                    print("inform player game over")

# ----------------------------------------------------------------------


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

    def clearDataBySeat(self, index, isOut=True):
        s = self.seats[index]
        if isOut:
            s.userId = 0
            s.entity = None
        s.ready = False
        s.score = 0
        s.position = {}
        s.direction = {}
        s.seatIndex = index

    def clearDataByEntityId(self, entityId, isOut=True):
        for i in range(len(self.seats)):
            if self.seats[i].userId == entityId:
                self.clearDataBySeat(i, isOut)
                break


class seat_roomInfo:
    def __init__(self, seatIndex):
        self.userId = 0
        self.score = 0
        self.position = {}
        self.entity = None
        self.direction = {}
        self.ready = False
        self.seatIndex = seatIndex
