# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *


class Account(KBEngine.Entity):
    def __init__(self):
        KBEngine.Entity.__init__(self)

    def LeaveRoom(self, callerEntityId):
        if callerEntityId != self.id:
            return
        KBEngine.globalData["Room_%i" % self.spaceID].ReqLeaveRoom(self)


    def playerReadyStateChange(self, state, seatIndex):
        self.isReady = state
        self.roomSeatIndex = seatIndex
        print("cell account playerReadyStateChange isReady:", self.isReady, "--seatIndex:", self.roomSeatIndex)




