import math
from time import sleep
import time
from typing import Callable, Literal
from core.CreviceRoom import CreviceRoom
from core.Room import Room
from core.Role import Direction, Role
from services import Controller, Screen, ScreenStream


class Dungeon:
    __ROOM_TARGET = "images/dungeons/room1.png"
    __ROOM_CREVICE_TARGET = "images/dungeons/room2.png"

    __roomList = {
        "3_0": {"nextRoomDirection": "Up", "first": True},
        "2_0": {"nextRoomDirection": "Right"},
        "2_1": {"nextRoomDirection": "Up"},
        "1_1": {"nextRoomDirection": "Up"},
        "0_1": {"nextRoomDirection": "Right"},
        "0_2": {"nextRoomDirection": "Right"},
        "boss": {"boss": True},
    }

    def __init__(
        self,
        name: str,
        area: str,
        target: str,
        offset: Controller.Offset | None,
        direction: Literal["Left", "Right"] = "Right",
    ):
        self.name = name
        self.area = area
        self.target = target
        self.offset = offset
        self.direction = direction
        self.__room: Room | None = None
        self.role = Role("images/roles/5.png")

        ScreenStream.register(self.__matchDungeonEntered)

    def into(self):
        self.__openMap()
        self.__transport()

    def __openMap(self):
        # 打开工会
        Controller.press(";")
        # 点击传送
        Controller.clickImg("images/transport.png")
        # 同意打开地图
        Controller.press("Space")
        # 点击世界地图
        Controller.clickImg("images/mapSelector.png")

    def __transport(self):
        # 点击目标区域
        Controller.clickImg(self.area)
        # 点击目的地
        Controller.clickImg(self.target, self.offset)
        # 同意传送
        Controller.press("Space")
        # 走向地下城
        Controller.press(self.direction, 3)

    def __matchDungeonEntered(self):
        started = ScreenStream.exist(self.__ROOM_TARGET)
        if started:
            self.role.buff()
            self.role.setup()
            ScreenStream.register(self.__matchRoom)
            ScreenStream.unregister(self.__matchDungeonEntered)

    def __matchBoss(self):
        boss = Screen.getFirstPoint(ScreenStream.match("images/dungeons/boss.png"))

        if boss:
            self.role.ticketAttack()

    def __finish(self):
        gift = Screen.getFirstPoint(ScreenStream.match("images/dungeons/gift.png"))
        count = 0
        if gift:
            print("战斗结束")
            time.sleep(0.5)
            Controller.press("Esc", 1)
            Controller.press("Esc", 1)
            Controller.press("Delete", 1)
            while count < 3:
                count += 1
                Controller.press("X")
            Controller.press("ShiftRight")
            self.__restart()

    def __createRoom(self, row: int, col: int, crevice: bool = False):
        point = f"{row}_{col}"
        if self.__room:
            if point == self.__room.getPoint():
                return
            else:
                self.__room.destroy()
        direction = self.__roomList[point]["nextRoomDirection"]

        if crevice:
            self.__room = CreviceRoom(self.role, row, col, direction)
        else:
            self.__room = Room(self.role, row, col, direction)

    def __createBossRoom(self):
        if self.__room:
            self.__room.destroy()
        ScreenStream.register(self.__matchBoss)
        ScreenStream.register(self.__finish)

    def __matchRoom(self):
        x = 1081
        y = 70
        size = 27
        area = (x, y, 1190, 180)
        locations = ScreenStream.match(self.__ROOM_TARGET, area)
        point = Screen.getFirstPoint(locations, area)
        crevice = False

        if not point:
            locations = ScreenStream.match(self.__ROOM_CREVICE_TARGET, area)
            point = Screen.getFirstPoint(locations, area)

            if point:
                crevice = True
            else:
                self.__createBossRoom()
                return

        roomX, roomY = point
        row = math.floor((roomY - y) / size)
        col = math.floor((roomX - x) / size)
        # print(point, row, col)
        self.__createRoom(row, col, crevice)

    def __restart(self):
        self.role.resetRefreshRoleLocationCount()
        ScreenStream.register(self.__matchDungeonEntered)
        ScreenStream.unregister(self.__matchBoss)
        ScreenStream.unregister(self.__finish)


if __name__ == "__main__":
    sleep(3)
    Controller.setup()

    dungeon = Dungeon(
        name="Silence",
        area="images/dungeons/1.png",
        target="images/dungeons/target.png",
        offset={"x": 50, "y": 50},
        direction="Right",
    )

    ScreenStream.listen()
    Controller.close()
