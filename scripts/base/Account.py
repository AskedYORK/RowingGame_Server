# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import Functor

MAIN_STATE_IDEL = 1
MAIN_STATE_MATCH = 2
MAIN_STATE_INGAME = 3


class Account(KBEngine.Proxy):
    def __init__(self):
        KBEngine.Proxy.__init__(self)
        self.MainState = MAIN_STATE_IDEL
        self.roomKey = 0

    def onTimer(self, id, userArg):
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        DEBUG_MSG(id, userArg)

    def onClientEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        INFO_MSG("account[%i] entities enable. entityCall:%s" % (self.id, self.client))

    def onLogOnAttempt(self, ip, port, password):
        """
        KBEngine method.
        客户端登陆失败时会回调到这里
        """
        INFO_MSG(ip, port, password)
        return KBEngine.LOG_ON_ACCEPT

    def onClientDeath(self):
        """
        KBEngine method.
        客户端对应实体已经销毁
        """
        DEBUG_MSG("Account[%i].onClientDeath:" % self.id)
        self.onLeaveRoom()
        # self.destroy()

    def reqCreateAvatar(self, name):
        '''
        客户端请求创建一个角色
        0:成功
        1:已有相同名字
        2:创建失败
        :param name:
        :return:
        '''
        if self.isNewPlayer == 0:
            self.client.OnReqCreateAvatar(2)
            return

        props = {
            "playerName": name,
        }
        print("reqCreateAvatar name:", name)
        nameEntity = KBEngine.createEntityLocally("CheckName", props)
        if nameEntity:
            nameEntity.writeToDB(Functor.Functor(self._OnNameSave, name))

    def _OnNameSave(self, name, success, avatar):
        print("_OnNameSave----name:",name, "--success:", success)
        if self.isDestroyed:
            if avatar:
                avatar.destroy()
            return
        if success:
            self.isNewPlayer = 0
            self.playerName_Base = name
            self.playerID_base = self.databaseID + 1000
            self.playerID = self.databaseID + 10000
            self.cellData["playerName"] = name
            self.cellData["playerID"] = self.playerID_base
            if self.client:
                self.client.OnReqCreateAvatar(0)
        else:
            self.client.OnReqCreateAvatar(1)

    def onLeaveRoom(self):
        self.destroyCellEntity()

    def enterMatchesMatch(self):
        if self.MainState != MAIN_STATE_IDEL:
            return
        self.MainState = MAIN_STATE_MATCH
        print("enterMatchesMatch----", self.cellData["position"], "---", self.cellData["direction"])
        KBEngine.globalData["Halls"].EnterMatchesMatch(self)

    def createCell(self, roomCellCallEntity):
        print("base account createCell roomCellCallEntity:", roomCellCallEntity)
        self.createCellEntity(roomCellCallEntity)

    def onLoseCell(self):
        self.MainState = MAIN_STATE_IDEL
        if self.client:
            self.client.playerLeaveRoom()

    def reqChangeRoom(self):
        KBEngine.globalData["Halls"].changeRoom(self, self.roomKey)

    def enterRoomSuccess(self, roomKey):
        print("base account enterRoomSuccess roomKey:", roomKey)
        self.roomKey = roomKey

    # 房间通知玩家换房间
    def OnTeleport(self, space):
        print("开始换房间，当前房间号---" + str(self.roomKey))
        self.teleport(space)

    # 换房间系统回调
    def onTeleportSuccess(self):
        print("换房间成功，当前房间号---" + str(self.roomKey))

    def GameCountDown(self, countDownTime):
        if self.client:
            self.client.GameCountDown(countDownTime)

    def GameStart(self):
        if self.client:
            self.client.GameStart()

    def GameOver(self):
        if self.client:
            self.client.GameOver()

    def PlayerFinishGame(self, entityId):
        if self.client:
            self.client.PlayerFinishGame(entityId);
