import math
from time import sleep
import time
from typing import Callable, Literal
from core import SelectRole, Sell
from core.CreviceRoom import CreviceRoom
from src.core.BossRoom import BossRoom
from src.core.MonsterRoom import MonsterRoom
from core.FirstRoom import FirstRoom
from core.Role import Direction, Role
from services import Controller, Screen, ScreenStream
from core import Roles_local as Roles
from src.core.Room import Room


class Dungeon:
    ROOM_TARGET = "images/dungeons/room1.png"
    __ROOM_CREVICE_TARGET = "images/dungeons/room2.png"
    __ROLE_TARGET = "images/dungeons/roleTarget.png"
    roomList = {
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
        ScreenStream.addListener(self.matchStatus)
        ScreenStream.addListener(self.matchDungeonCard)

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
        entered = ScreenStream.exist(self.ROOM_TARGET)

        if not entered:
            return

        self.role.buff()
        self.role.setup()
        return ScreenStream.addListener(self.matchRoom)

    def matchStatus(self):
        if not self.room:
            return

        if time.time() - self.room.startTime < 90:
            return

        print("超时")
        self.backCity()

    def createRoom(self, row: int, col: int, crevice: bool = False):
        id = f"{row}_{col}"
        if self.room:
            if id == self.room.id:
                return
            else:
                self.room.destroy()

        if id in self.roomList:
            room = self.roomList[id]
            direction = room["nextRoomDirection"]
            if "first" in room:
                self.room = FirstRoom(id, self.role, direction)
            elif crevice:
                self.room = CreviceRoom(id, self.role, direction, self.createBossRoom)
            else:
                self.room = MonsterRoom(id, self.role, direction)
        else:
            self.backCity()

    def createBossRoom(self):
        if self.room:
            self.room.destroy()

        self.finishCount += 1
        self.room = BossRoom(
            "Boss", self.role, self.matchRoleEnd, self.finishCount > 10
        )

    def matchRoom(self):
        x = 1081
        y = 70
        size = 27
        area = (x, y, 1190, 180)
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
        ScreenStream.addListener(self.matchDungeonEntered)

    def backCity(self):
        print("返回城镇")

        self.destroyRoom()

        Controller.mouseMove(10, 10)
        Controller.press("Esc")
        sleep(1)
        Controller.clickImg("images/backCity.png")
        sleep(1)

        if Screen.exist("images/confirm.png"):
            Controller.press("Space")
            # ScreenStream.addListener(self.__matchInCity)

    def matchRoleEnd(self):
        isEnd = Screen.exist("images/dungeons/end.png")
        if isEnd:
            print("疲劳已用光", isEnd)
            self.switchRole()
        else:
            self.reenterDungeon()

    def switchRole(self):
        self.backCity()
        # TODO：有待调整，扔需要持续检测
        ScreenStream.clear()
        time.sleep(2)
        Sell.backCelia()
        Sell.openStore()
        SelectRole.toSelectRole()

    def destroyRoom(self):
        if self.room:
            self.room.destroy()
            self.room = None


if __name__ == "__main__":
    Controller.setup()

    dungeon = Dungeon(
        name="Silence",
        area="images/dungeons/1.png",
        target="images/dungeons/target.png",
        offset={"x": 50, "y": 50},
        roleOption=Roles.roleList[3],
        direction="Right",
    )

    ScreenStream.listen()
    Controller.close()
