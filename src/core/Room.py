import os
from threading import Thread
import threading
import time
from typing import Literal
from core.Role import Direction, Role
from services import Controller, Screen, ScreenStream


class Room:
    __DROP_BASE_PATH = "images/drops/"
    __MONSTER_BASE_PATH = "images/monsters/"
    __COUNTER_BASE_PATH = "images/counter/"
    __DOOR = "images/dungeons/door2.png"
    __RELEASE = "images/dungeons/empty.png"

    def __init__(
        self,
        role: Role,
        row: int,
        col: int,
        nextRoomDirection: Direction,
    ):
        self.__role = role
        self.__row = row
        self.__col = col
        self.__nextRoomDirection: Direction = nextRoomDirection

        # 初始化房间状态
        self.__released = False
        self.__matchDoorCount = 0
        self.__roleLocked = False
        # 卡住的假象
        self.__falseLocked = True
        self.__hasCounter = False
        self.__noDropList = False
        self.__mainDirectionNotGo = True
        self.__matchDoorSecondaryDirection: Direction | None = None

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
        ScreenStream.register(self.__matchRoomRelease)

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
    def __matchRoomRelease(self):
        point = Screen.getFirstPoint(ScreenStream.match(self.__RELEASE))
        self.__released = point is not None

        if not point:
            point = Screen.getFirstPoint(ScreenStream.match(self.__DOOR))
            self.__released = point is not None

        if self.__released:
            ScreenStream.unregister(self.__matchMonsterList)
            ScreenStream.register(self.__matchCounterList)
            if not self.__noDropList:
                ScreenStream.register(self.__matchDropList)
        else:
            ScreenStream.unregister(self.__matchDropList)
            ScreenStream.unregister(self.__matchNextRoomDoor)
            ScreenStream.register(self.__matchMonsterList)

    def __refreshRolePosition(self):
        self.__role.refreshRoleLocation()

    def __matchMonsterList(self):
        self.__monsterPointList = []
        self.__monsterThreadList = []

        for monster in self.__monsterList:
            thread = threading.Thread(target=self.__matchMonster, args=(monster,))
            thread.start()
            self.__monsterThreadList.append(thread)

        for thread in self.__monsterThreadList:
            thread.join()

        if len(self.__monsterPointList) > 0:
            self.__role.attack(self.__monsterPointList, {"x": 800, "y": 120})
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

    def __matchDropList(self):
        self.__dropThreadList = []
        self.__dropPointList = []

        for drop in self.__dropList:
            thread = threading.Thread(target=self.__matchDrop, args=(drop,))
            thread.start()
            self.__dropThreadList.append(thread)

        for thread in self.__dropThreadList:
            thread.join()

        if len(self.__dropPointList) > 0:
            self.__role.pickUp(self.__dropPointList)
        else:
            self.__noDropList = True
            ScreenStream.unregister(self.__matchDropList)
            ScreenStream.register(self.__matchNextRoomDoor)

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
            ScreenStream.unregister(self.__matchDropList)
            ScreenStream.unregister(self.__matchNextRoomDoor)

    def __matchCounter(self, target: str):
        point = Screen.getFirstPoint(ScreenStream.match(target))

        if not point:
            return

        point = (point[0] + 15, point[1] + 15)
        self.__counterPointList.append(point)

    def __matchNextRoomDoor(self):
        if self.__hasCounter:
            return

        if self.__nextRoomDirection == "Right" or self.__nextRoomDirection == "Left":
            self.__matchHorizontalDoor()

        if self.__nextRoomDirection == "Up" or self.__nextRoomDirection == "Down":
            self.__matchVerticalDoor()

    def __matchHorizontalDoor(self):
        roleX, roleY = self.__role.getPoint()
        vMedium = 687

        if abs(roleY - vMedium) > 50 and self.__matchDoorCount == 0:
            direction = roleY > vMedium and "Up" or "Down"
            self.__role.move(direction, 0.1)
        else:
            if self.__mainDirectionNotGo:
                print("第一次在主方向移动")
                self.__mainDirectionNotGo = False
                self.__role.move(self.__nextRoomDirection, 1.5)
            elif self.__role.checkLock():
                print("角色卡住")
                # 检测卡住的竖直方向
                self.__roleLocked = True
                direction = self.__matchDoorSecondaryDirection or "Down"
                direction = direction == "Up" and "Down" or "Up"
                self.__matchDoorCount += 1
                self.__matchDoorSecondaryDirection = direction
                self.__role.move(f"{direction} {self.__nextRoomDirection}", 1.5)  # type: ignore
            elif self.__roleLocked:
                print("角色在主方向卡住")
                direction = self.__matchDoorSecondaryDirection
                self.__matchDoorCount += 1
                self.__role.move(f"{direction} {self.__nextRoomDirection}", 1.5)  # type: ignore
            else:
                print("主方向没有卡住")
                self.__role.move(self.__nextRoomDirection, 1.5)

    def __matchVerticalDoor(self):
        roleX, roleY = self.__role.getPoint()
        hMedium = 600

        if abs(roleX - hMedium) > 50 and self.__matchDoorCount == 0:
            direction = roleX > hMedium and "Left" or "Right"
            self.__role.move(direction, 0.1)
        else:
            if self.__mainDirectionNotGo:
                self.__mainDirectionNotGo = False
                self.__role.move(self.__nextRoomDirection, 1.5)
            elif self.__role.checkLock():
                print("角色卡住")
                self.__roleLocked = True
                direction = self.__matchDoorSecondaryDirection or "Right"
                direction = direction == "Right" and "Left" or "Right"
                self.__matchDoorCount += 1
                self.__matchDoorSecondaryDirection = direction
                self.__role.move(f"{direction} {self.__nextRoomDirection}", 1.5)  # type: ignore
            elif self.__roleLocked:
                print("角色在主方向卡住")
                direction = self.__matchDoorSecondaryDirection
                self.__matchDoorCount += 1
                self.__role.move(f"{direction} {self.__nextRoomDirection}", 1.5)  # type: ignore
            else:
                self.__role.move(self.__nextRoomDirection, 1.5)

    def __unregisterMatcher(self):
        ScreenStream.unregister(self.__matchRoomRelease)
        ScreenStream.unregister(self.__matchMonsterList)
        ScreenStream.unregister(self.__matchDropList)
        ScreenStream.unregister(self.__matchNextRoomDoor)

    def destroy(self):
        self.__unregisterMatcher()

    def getPoint(self):
        return f"{self.__row}_{self.__col}"


if __name__ == "__main__":
    time.sleep(2)
    Controller.setup()
    role = Role("images/roles/3.png")
    room = Room(role, 3, 0, "Right")
    ScreenStream.listen()
    Controller.release()
    Controller.close()
