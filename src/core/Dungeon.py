import math
from time import sleep
import time
from typing import Callable, Literal

import cv2
from constants.DNFConfig_local import REENTER
from core import SelectRole, Sell
from core import System
from core.CreviceRoom import CreviceRoom
from core.BossRoom import BossRoom
from core.MonsterRoom import MonsterRoom
from core.FirstRoom import FirstRoom
from core.Role import Direction, Role
from core.System import closeSystemSetting
from services import Controller, Logger, Screen, ScreenStream
from core import Roles_local as Roles
from core.Room import Room


class Dungeon:
    ROOM_TARGET = "images/dungeons/room3.png"
    __ROOM_CREVICE_TARGET = "images/dungeons/room2.png"
    __ROLE_TARGET = "images/dungeons/roleTarget.png"
    roomList = {
        "1_0": {"nextRoomDirection": "Right", "first": True},
        "1_1": {"nextRoomDirection": "Right"},
        "1_2": {"nextRoomDirection": "Right"},
        "1_3": {"nextRoomDirection": "Right"},
        "1_4": {"nextRoomDirection": "Right"},
        # "0_2": {"nextRoomDirection": "Right"},
        "boss": {"boss": True},
    }

    def __init__(
        self,
        name: str,
        area: str,
        target: str,
        offset: Controller.Offset | None,
        roleOption,
        direction: Literal["Left", "Right"] = "Right",
    ):
        self.name = name
        self.area = area
        self.target = target
        self.offset = offset
        self.direction = direction
        self.room: Room | None = None
        self.role = Role(self.__ROLE_TARGET, roleOption)
        self.finishCount = 0
        self.needSwitchRole = False

    def into(self):
        self.__openMap()
        self.__transport()

    def __openMap(self):
        # 打开工会
        Controller.press(";")
        # 点击传送
        Controller.clickImg("images/transport.png", {"x": 20, "y": 20})
        # 同意打开地图
        Controller.press(
            "Space",
        )
        # 点击世界地图
        Controller.clickImg("images/mapSelector.png", {"x": 10, "y": 10})

    def __transport(self):
        # 点击目标区域
        Controller.clickImg(self.area)
        # 点击目的地
        Controller.clickImg(self.target, self.offset)
        # 同意传送
        Controller.press("Space")
        sleep(1)
        self.moveToDungeonList()

    def moveToDungeonList(self):
        # 走向地下城
        Controller.press(self.direction, 3)
        ScreenStream.addListener(self.matchDungeonCard)

    def matchDungeonCard(self):
        existLarge = ScreenStream.exist("images/dungeons/targetLarge.png")

        if not existLarge:
            locations = ScreenStream.match("images/dungeons/target.png")
            point = Screen.getFirstPoint(locations)

            if not point:
                return
            else:
                Controller.click(locations)

        Controller.press("Space")
        return ScreenStream.addListener(self.matchDungeonEntered)

    def matchDungeonEntered(self):
        point = Screen.getFirstPoint(ScreenStream.match(self.ROOM_TARGET))

        if not point:
            return

        (x, y) = point

        if x < 1028:
            return

        self.role.buff()
        self.role.setup()

        ScreenStream.addListener(self.matchStatus)
        return ScreenStream.addListener(self.matchRoom)

    def matchStatus(self):
        if not self.room:
            return

        if time.time() - self.room.startTime < 90:
            return

        Logger.log("超时")
        self.backCity()

    def createRoom(self, row: int, col: int, crevice: bool = False):
        id = f"{row}_{col}"
        if self.room:
            if id == "Boss":
                self.room.destroy()
            elif id == self.room.id:
                return
            else:
                self.room.destroy()

        if id in self.roomList:
            room = self.roomList[id]
            direction = room["nextRoomDirection"]

            if crevice:
                self.room = CreviceRoom(id, self.role, direction, self.createBossRoom)
            else:
                self.room = MonsterRoom(id, self.role, direction)
        else:
            self.backCity()

    def createBossRoom(self):
        if self.room:
            if self.room.id == "Boss":
                return
            else:
                self.room.destroy()

        self.finishCount += 1
        self.room = BossRoom(
            "Boss", self.role, self.matchRoleEnd, self.finishCount > 10
        )
        if self.finishCount > 10:
            self.finishCount = 0

    def matchRoom(self):
        x = 1028
        y = 64
        size = 27
        area = (x, y, 1190, 145)
        locations = ScreenStream.match(self.ROOM_TARGET, area)
        point = Screen.getFirstPoint(locations, area)
        crevice = False

        if not point:
            locations = ScreenStream.match(self.__ROOM_CREVICE_TARGET, area)
            point = Screen.getFirstPoint(locations, area)

            if point:
                crevice = True
            else:
                self.createBossRoom()
                return

        roomX, roomY = point
        row = math.floor((roomY - y) / size)
        col = math.floor((roomX - x) / size)
        self.createRoom(row, col, crevice)

    def reenterDungeon(self):
        self.destroyRoom()
        self.role.resetRefreshRoleLocationCount()
        Controller.press(REENTER)  # type: ignore
        ScreenStream.removeListener(self.matchRoom)
        ScreenStream.addListener(self.matchDungeonEntered)

    def backCity(self):
        Logger.log("返回城镇")

        self.destroyRoom()

        System.openSystemSetting()
        Controller.clickImg("images/backCity.png")
        sleep(1)

        if Screen.exist("images/confirm.png"):
            Controller.press("Space")

    def matchRoleEnd(self):
        roleEnd = ScreenStream.exist("images/dungeons/roleEnd.png")

        if roleEnd:
            Logger.log("疲劳已用光", roleEnd)
            self.switchRole()
        else:
            Logger.log("重新挑战")
            self.reenterDungeon()

    def switchRole(self):
        self.needSwitchRole = True
        self.removeListenerList()
        self.backCity()

    def backCelia(self):
        # 此处通过调用关闭系统菜单，来达到关闭广告弹窗的效果
        Sell.backCelia()
        SelectRole.toSelectRole()
        ScreenStream.stop()

    def destroyRoom(self):
        if self.room:
            self.room.destroy()
            self.room = None

    def removeListenerList(self):
        ScreenStream.removeListener(self.matchStatus)
        ScreenStream.removeListener(self.matchDungeonCard)
        ScreenStream.removeListener(self.matchDungeonEntered)
        ScreenStream.removeListener(self.matchRoom)


if __name__ == "__main__":
    # Controller.setup()

    # dungeon = Dungeon(
    #     name="Silence",
    #     area="images/dungeons/1.png",
    #     target="images/dungeons/target.png",
    #     offset={"x": 50, "y": 50},
    #     roleOption=Roles.roleList[3],
    #     direction="Right",
    # )

    # ScreenStream.listen()
    # Controller.close()
    def room():
        point = Screen.getFirstPoint(ScreenStream.match("images/dungeons/room3.png"))
        print(point)

    ScreenStream.addListener(room)
    ScreenStream.listen()
