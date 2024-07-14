import os
from threading import Thread
import threading
import time
from core import Roles_local
from core.Role import Direction, Role
from services import Controller, Screen, ScreenStream
from core.Room import Room
from services.Scene import Scene


class MonsterRoom(Room):
    __DROP_BASE_PATH = "images/drops/"
    __MONSTER_BASE_PATH = "images/monsters/"
    __COUNTER_BASE_PATH = "images/counter/"
    DOOR = "images/dungeons/door2.png"
    RELEASE = "images/dungeons/empty.png"

    def __init__(self, id: str, role: Role, nextRoomDirection: Direction, door: str):
        super().__init__(id, role)

        self.nextRoomDirection: Direction = nextRoomDirection

        # 初始化房间状态
        self.released = False
        self.door = door
        self.__matchDoorCount = 0
        self.__roleLocked = False
        self.__hasCounter = False
        self.__noDropList = False
        self.__mainDirectionNotGo = True
        self.__matchDoorSecondaryDirection: Direction | None = None
        self.__firstMove = False

        # 声明怪物列表系列变量
        self.__monsterList: list[str] = []
        self.__monsterThreadList: list[Thread] = []
        self.__monsterPointList: list[Screen.Point] = []

        # 声明掉落物列表系列变量
        self.__dropList: list[str] = []
        self.__dropThreadList: list[Thread] = []
        self.__dropPointList: list[Screen.Point] = []

        # 声明计数器列表系列变量
        self.__counterList: list[str] = []
        self.__counterThreadList: list[Thread] = []
        self.__counterPointList: list[Screen.Point] = []

        # 初始化怪物列表
        self.__initMonsterList()

        # 初始化掉落物列表
        self.__initDropList()

        self.__initCounterList()

        # 监听房间是否可以同行
        ScreenStream.addListener(self.matchNextRoomDoor)

    def __initMonsterList(self):
        self.__monsterList = list(
            map(
                lambda path: self.__MONSTER_BASE_PATH + path,
                os.listdir(self.__MONSTER_BASE_PATH),
            )
        )

    def __initDropList(self):
        self.__dropList = list(
            map(
                lambda path: self.__DROP_BASE_PATH + path,
                os.listdir(self.__DROP_BASE_PATH),
            )
        )

    def __initCounterList(self):
        self.__counterList = list(
            map(
                lambda path: self.__COUNTER_BASE_PATH + path,
                os.listdir(self.__COUNTER_BASE_PATH),
            )
        )

    # 检查房间是否已可以同行，即怪物已全部清除
    def matchRoomStatus(self):
        point = Screen.getFirstPoint(ScreenStream.match(self.RELEASE))
        self.released = point is not None

        if not point:
            point = Screen.getFirstPoint(ScreenStream.match(self.DOOR))
            self.released = point is not None

        if self.released:
            ScreenStream.removeListener(self.moveToVerticalCenter)
            ScreenStream.removeListener(self.matchMonsterList)
            ScreenStream.addListener(self.__matchCounterList)
            if not self.__noDropList:
                ScreenStream.addListener(self.matchDropList)
        else:
            ScreenStream.removeListener(self.matchDropList)
            ScreenStream.removeListener(self.searchNextRoomDoor)
            if not self.__firstMove:
                ScreenStream.addListener(self.moveToVerticalCenter)

    def __refreshRolePosition(self):
        self.role.refreshRoleLocation()

    def matchMonsterList(self):
        self.__monsterPointList = []
        self.__monsterThreadList = []

        for monster in self.__monsterList:
            thread = threading.Thread(target=self.__matchMonster, args=(monster,))
            thread.start()
            self.__monsterThreadList.append(thread)

        for thread in self.__monsterThreadList:
            thread.join()

        if len(self.__monsterPointList) > 0:
            self.role.attack(self.__monsterPointList, (800, 120))
        else:
            self.__refreshRolePosition()

    def __matchMonster(self, monster: str):
        area = (0, 230, 1200, 900)
        locations = ScreenStream.match(monster, area)
        point = Screen.getFirstPoint(locations, area)

        if not point:
            return

        point = (point[0], point[1] + 100)
        self.__monsterPointList.append(point)

    def matchDropList(self):
        self.__dropThreadList = []
        self.__dropPointList = []

        for drop in self.__dropList:
            thread = threading.Thread(target=self.__matchDrop, args=(drop,))
            thread.start()
            self.__dropThreadList.append(thread)

        for thread in self.__dropThreadList:
            thread.join()

        if len(self.__dropPointList) > 0:
            self.role.pickUp(self.__dropPointList)
        else:
            self.__noDropList = True
            return ScreenStream.addListener(self.matchNextRoomDoor)

    def __matchDrop(self, target: str):
        point = Screen.getFirstPoint(ScreenStream.match(target))

        if not point:
            return

        point = (point[0] + 15, point[1] + 15)
        self.__dropPointList.append(point)

    def __matchCounterList(self):
        self.__counterThreadList = []
        self.__counterPointList = []

        for drop in self.__counterList:
            thread = threading.Thread(target=self.__matchCounter, args=(drop,))
            thread.start()
            self.__counterThreadList.append(thread)

        for thread in self.__counterThreadList:
            thread.join()

        if len(self.__counterPointList) > 0:
            # 有计数器
            self.__hasCounter = True
            ScreenStream.removeListener(self.matchDropList)
            ScreenStream.removeListener(self.searchNextRoomDoor)

    def __matchCounter(self, target: str):
        point = Screen.getFirstPoint(ScreenStream.match(target))

        if not point:
            return

        point = (point[0] + 15, point[1] + 15)
        self.__counterPointList.append(point)

    def moveToVerticalCenter(self):
        roleX, roleY = self.role.getPoint()
        vMedium = 687

        if abs(roleY - vMedium) > 80 and self.__matchDoorCount == 0:
            direction = roleY > vMedium and "Up" or "Down"
            self.role.move(direction, self.role.speed)
        else:
            self.role.move("Right", 0.01)
            self.role.skillAttack()
            self.__firstMove = True
            return ScreenStream.addListener(self.matchMonsterList)

    def matchNextRoomDoor(self):
        # name = "下一个房间"
        # target = self.door
        # scene = Scene(name, target, onMatched=self.handleNextRoomDoorMatched)
        # scene.setup()
        point = Screen.getFirstPoint(ScreenStream.match(self.door))
        if point:
            self.handleNextRoomDoorMatched(point, None)
        else:
            Controller.release()
            self.searchNextRoomDoor()

    def handleNextRoomDoorMatched(self, point: Screen.Point, l):
        self.role.go(point)
        # Controller.press("Right")

    def searchNextRoomDoor(self):
        if self.__hasCounter:
            return

        if self.nextRoomDirection == "Right" or self.nextRoomDirection == "Left":
            self.__searchHorizontalDoor()

        if self.nextRoomDirection == "Up" or self.nextRoomDirection == "Down":
            self.__searchVerticalDoor()

    def __searchHorizontalDoor(self):
        roleX, roleY = self.role.getPoint()
        vMedium = 687

        if abs(roleY - vMedium) > 50 and self.__matchDoorCount == 0:
            direction = roleY > vMedium and "Up" or "Down"
            self.role.move(direction)
        else:
            self.role.move(self.nextRoomDirection)

    def __searchVerticalDoor(self):
        roleX, roleY = self.role.getPoint()
        hMedium = 600

        if abs(roleX - hMedium) > 50 and self.__matchDoorCount == 0:
            direction = roleX > hMedium and "Left" or "Right"
            self.role.move(direction)
        else:
            self.role.move(self.nextRoomDirection)

    def unregisterMatcher(self):
        ScreenStream.removeListener(self.matchRoomStatus)
        ScreenStream.removeListener(self.matchMonsterList)
        ScreenStream.removeListener(self.matchDropList)
        ScreenStream.removeListener(self.searchNextRoomDoor)
        ScreenStream.removeListener(self.__matchCounterList)
        ScreenStream.removeListener(self.moveToVerticalCenter)

    def destroy(self):
        self.unregisterMatcher()


if __name__ == "__main__":
    try:
        Controller.setup()
        role = Role("images/dungeons/roleTarget.png", Roles_local.roleList[0])
        role.setup()
        room = MonsterRoom("2_0", role, "Right", "images/dungeons/door2.png")

        ScreenStream.listen()
        Controller.close()
    except Exception as error:
        Controller.close()
        print("程序异常退出", error)
    except:
        Controller.close()
