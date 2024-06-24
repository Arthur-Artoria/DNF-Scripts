import math
from time import sleep
import time
from typing import Callable, Literal
from core import SelectRole, Sell
from core.CreviceRoom import CreviceRoom
from core.Room import Room
from core.FirstRoom import FirstRoom
from core.Role import Direction, Role
from services import Controller, Screen, ScreenStream
from core import Roles_local as Roles


class Dungeon:
    __ROOM_TARGET = "images/dungeons/room1.png"
    __ROOM_CREVICE_TARGET = "images/dungeons/room2.png"
    __ROLE_TARGET = "images/dungeons/roleTarget.png"
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
        roleOption,
        direction: Literal["Left", "Right"] = "Right",
    ):
        self.name = name
        self.area = area
        self.target = target
        self.offset = offset
        self.direction = direction
        self.__room: Room | None = None
        self.role = Role(self.__ROLE_TARGET, roleOption)
        self.__count = 0
        self.__bossTime = None
        ScreenStream.register(self.__matchStatus)
        ScreenStream.register(self.__matchDungeonsCard)

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
        self.__goToDungeon()

    def __goToDungeon(self):
        # 走向地下城
        Controller.press(self.direction, 3)
        ScreenStream.register(self.__matchDungeonsCard)

    def __matchDungeonsCard(self):
        locations = ScreenStream.match("images/dungeons/target.png")
        point = Screen.getFirstPoint(locations)

        if point:
            Controller.click(locations)
            Controller.press("Space")

        locations = ScreenStream.match("images/dungeons/targetLarge.png")
        point = Screen.getFirstPoint(locations)

        if point:
            Controller.press("Space")

        ScreenStream.register(self.__matchDungeonEntered)

    def __matchDungeonEntered(self):
        started = ScreenStream.exist(self.__ROOM_TARGET)
        if started:
            self.role.buff()
            self.role.setup()
            ScreenStream.register(self.__matchRoom)
            ScreenStream.unregister(self.__matchDungeonsCard)
            ScreenStream.unregister(self.__matchDungeonEntered)

    def __matchStatus(self):
        if self.__room:
            if time.time() - self.__room.startTime > 90:
                print("超时")
                self.__room.destroy()
                self.__room = None
                self.__backCity()
        elif self.__bossTime:
            if time.time() - self.__bossTime > 90:
                print("超时")
                self.__bossTime = None
                self.__backCity()

    def __matchWeakness(self):
        locations = ScreenStream.match("images/weakness.png")
        point = Screen.getFirstPoint(locations)
        if point:
            Controller.click(locations)
            sleep(1)
            Controller.clickImg("images/weaknessConfirm.png")
            sleep(1)
            self.__goToDungeon()
            return True

    def __matchBoss(self):
        boss = Screen.getFirstPoint(ScreenStream.match("images/dungeons/boss.png"))

        if boss:
            self.role.ticketAttack()

    def __finish(self):
        gift = Screen.getFirstPoint(ScreenStream.match("images/dungeons/gift.png"))
        if gift:
            print("战斗结束")
            time.sleep(0.5)
            self.__count += 1
            Controller.press("Esc")
            sleep(1)
            if self.__count > 10:
                Sell.sell()
            else:
                Controller.press("Esc")
                sleep(1)
            Controller.press("Delete")
            Controller.press("X", 3)
            Controller.press("ShiftRight")
            time.sleep(1)
            self.matchRoleEnd()

    def __createRoom(self, row: int, col: int, crevice: bool = False):
        point = f"{row}_{col}"
        if self.__room:
            if point == self.__room.getPoint():
                return
            else:
                self.__room.destroy()

        if point in self.__roomList:
            room = self.__roomList[point]
            direction = room["nextRoomDirection"]
            if "first" in room:
                self.__room = FirstRoom(self.role, row, col, direction)
            elif crevice:
                print("裂缝房间")
                self.__room = CreviceRoom(self.role, row, col, direction)
            else:
                self.__room = Room(self.role, row, col, direction)
        else:
            self.__backCity()

    def __createBossRoom(self):
        if self.__room:
            self.__room.destroy()
            self.__room = None

        self.__bossTime = time.time()
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
        self.__createRoom(row, col, crevice)

    def __restart(self):
        self.role.resetRefreshRoleLocationCount()
        ScreenStream.register(self.__matchDungeonEntered)
        ScreenStream.unregister(self.__matchBoss)
        ScreenStream.unregister(self.__finish)

    def __backCity(self):
        print("返回城镇")
        Controller.mouseMove(10, 10)
        Controller.press("Esc")
        sleep(1)
        Controller.clickImg("images/backCity.png")
        sleep(1)

        if Screen.exist("images/confirm.png"):
            Controller.press("Space")
            ScreenStream.register(self.__matchInCity)

    def __matchInCity(self):
        isInCity = ScreenStream.exist("images/city.png")
        if isInCity:
            sleep(1)
            ScreenStream.register(self.__matchWeakness)
            return True

    def matchRoleEnd(self):
        isEnd = Screen.exist("images/dungeons/end.png")
        print("疲劳已用光", isEnd)
        if isEnd:
            self.__backCity()
            ScreenStream.stop()
            time.sleep(2)
            Sell.backCelia()
            Sell.openStore()
            SelectRole.toSelectRole()
        else:
            self.__restart()


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

    ScreenStream.register(dungeon.matchRoleEnd)

    ScreenStream.listen()
    Controller.close()
