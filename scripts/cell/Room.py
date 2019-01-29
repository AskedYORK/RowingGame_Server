# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

COUNT_DOWN_TIME = 5
COUNT_DOWN_TIME_GAME_END = 60

COUNT_DOWN_TIME_TAG = 10
COUNT_DOWN_TIME_END_TAG = 2
MAX_PLAYER_NEED_CAN_START = 1


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

    def check_room_can_start(self):
        ready_count = 0
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.ready:
                ready_count += 1
        if ready_count < MAX_PLAYER_NEED_CAN_START:
            print("cell room has player not ready---")
            return

        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.entity is not None:
                seat.entity.GameCountDown(COUNT_DOWN_TIME_TAG)
                print("inform all client GameCountDown")
        self.addTimer(0.1, 1, COUNT_DOWN_TIME_TAG)

    def reqChangeReadyState(self, callerEntityID, STATE):
        print("cell room reqChangeReadyState---callerEntityID", callerEntityID, "--STATE:", STATE)
        # 设置座位上玩家的状态
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.userId == callerEntityID:
                seat.ready = not STATE
                if seat.entity is not None:
                    seat.entity.cell.playerReadyStateChange(seat.ready, seat.seatIndex)
                    print("reqChangeReadyState:", seat.ready, "--index:", seat.seatIndex)
                    break

        self.check_room_can_start()

        # for i in range(len(self.roomInfo.seats)):
        #     seat = self.roomInfo.seats[i];
        #     if not seat.ready:
        #         print("cell room has player not ready---", seat.userId, "---", seat.ready)
        #         return
        #
        # for i in range(len(self.roomInfo.seats)):
        #     seat = self.roomInfo.seats[i]
        #     seat.entity.GameCountDown(COUNT_DOWN_TIME_TAG)
        #     print("inform all client GameCountDown")
        #
        # self.addTimer(0.1, 1, COUNT_DOWN_TIME_TAG)

    def PlayerFinishGame(self, entityId):
        # 只要有玩家完成比赛就把倒计时置为0，结束比赛
        self.finishGameCount += 1
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.entity is not None:
                seat.entity.PlayerFinishGame(entityId)
                self.endTime = 0

        # # 所有玩家完成比赛
        # if self.finishGameCount == len(self.roomInfo.seats):
        #     self.endTime = 0

    def onTimer(self, id, userArg):
        # 游戏开始倒计时
        if COUNT_DOWN_TIME_TAG == userArg:
            if self.countDown < COUNT_DOWN_TIME:
                self.countDown += 1
                # 倒计时通知每一个玩家
                for i in range(len(self.roomInfo.seats)):
                    seat = self.roomInfo.seats[i]
                    if seat.entity is not None:
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
                    if seat.entity is not None:
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
                # 倒计时完了，通知每一个玩家游戏结束
                print("game over")
                for i in range(len(self.roomInfo.seats)):
                    seat = self.roomInfo.seats[i]
                    if seat.entity is not None:
                        seat.ready = False
                        seat.entity.cell.playerReadyStateChange(False, seat.seatIndex)
                        seat.entity.GameOver()
                        print("inform player game over")

    def player_update(self, entity_id, position, direction, speed):
        # if not self.IsGameStart:
        #     return
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.entity is not None and seat.userId != 0:
                # 更新自己的位置相关信息
                if seat.userId == entity_id:
                    seat.entity.cell.player_update(position, direction, speed)
                else:
                    # 通知房间玩家位置变动
                    seat.entity.update_pos_to_client(entity_id, position, direction, speed)

    def player_wheel(self, entity_id, direction, play):
        """
        玩家转向
        :param entity_id:
        :param direction:
        :param play:
        :return:
        """
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.entity is not None and seat.userId != 0:
                # 更新自己的位置相关信息
                if seat.userId != entity_id:
                    # 通知玩家转向
                    seat.entity.player_wheel_to_client(entity_id, direction, play)

    def player_5g_info(self, entity_id, sore, m_bps, delay, frame):
        """
        传输得分、帧率的信息
        :param entity_id:
        :param sore:
        :param m_bps:
        :param delay:
        :param frame:
        :return:
        """
        for i in range(len(self.roomInfo.seats)):
            seat = self.roomInfo.seats[i]
            if seat.entity is not None and seat.userId != 0:
                # 更新自己的位置相关信息
                if seat.userId != entity_id:
                    # 通知玩家转向
                    seat.entity.player_5g_info_to_client(entity_id, sore, m_bps, delay, frame)


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
