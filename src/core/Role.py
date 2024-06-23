from ast import While
from time import sleep
import time
from typing import Literal
from services import Controller, Screen, ScreenStream
from constants import Monitor

type Direction = Literal[
    "Up", "Down", "Left", "Right", "Up Left", "Up Right", "Down Left", "Down Right"
]


class Role:
    # TODO: 临时方案，后续需要优化
    # 旅人
    # __offset: tuple = (20, 180)

    # 奶妈
    __offset: tuple = (20, 200)

    __refreshRoleLocationDirectionList: list[Direction] = [
        "Down Right",
        "Up Right",
        "Down Left",
        "Up Left",
    ]

    __skillList = [
        # 旅人
        # {"key": "A", "CD": 5.8, "dispatch": 0, "duration": 0.5},
        # {"key": "Q", "CD": 10, "dispatch": 0, "duration": 0.5},
        # {"key": "S", "CD": 11.2, "dispatch": 0, "duration": 0.5},
        # {"key": "W", "CD": 12.4, "dispatch": 0, "duration": 0.5},
        # {"key": "D", "CD": 27.7, "dispatch": 0, "duration": 0.5},
        # {"key": "R", "CD": 37.2, "dispatch": 0, "duration": 0.5},
        # 奶妈
        # {"key": "F", "CD": 12, "dispatch": 0, "duration": 0.5},
        {"key": "D", "CD": 12, "dispatch": 0, "duration": 2},
        {"key": "A", "CD": 9, "dispatch": 0, "duration": 0.5},
        {"key": "E", "CD": 6, "dispatch": 0, "duration": 0.5},
        {"key": "Q", "CD": 12, "dispatch": 0, "duration": 0.5},
        {"key": "S", "CD": 5.4, "dispatch": 0, "duration": 0.5},
        {"key": "W", "CD": 15, "dispatch": 0, "duration": 0.5},
        {"key": "R", "CD": 13.5, "dispatch": 0, "duration": 0.5},
    ]

    # __ticket = {"key": "Up Down Space", "CD": 275, "dispatch": 0, "duration": 5}
    __ticket = {"key": "V", "CD": 275, "dispatch": 0, "duration": 6}

    __refreshRoleLocationCount = 0

    def __init__(self, target: str):
        self.target = target
        self.point: Screen.Point | None = None
        self.prevPoint: Screen.Point | None = None

        ScreenStream.register(self.setRoleLocation)

    def getPoint(self) -> Screen.Point:
        if not self.point:
            self.__lookForRole()

        return self.point  # type: ignore

    def __updateRoleLocation(self, locations):
        offsetX, offsetY = self.__offset

        # 没匹配到图片直接返回
        if not locations:
            self.point = None
            return

        point = Screen.getFirstPoint(locations)

        # 没匹配到点直接返回
        if not point:
            self.point = None
            return

        x, y = point
        self.prevPoint = self.point
        self.point = (x + offsetX, y + offsetY)
        print("上一次角色位置：", self.prevPoint, "当前角色位置：", self.point)

    def setRoleLocation(self):
        self.__updateRoleLocation(ScreenStream.match(self.target))

    def syncSetRoleLocation(self):
        time.sleep(0.5)
        self.__updateRoleLocation(Screen.match(self.target))

    def move(self, direction: Direction, seconds: float = 0.5):
        Controller.press(direction, seconds)

    # 尝试向不同方向移动角色各一次
    def __lookForRole(self):
        count = 0
        directionList: list[Direction] = ["Up", "Down", "Left", "Right"]
        directionLen = len(directionList)

        Screen.updateMonitor(Monitor.DNF_MONITOR)

        while not self.point:
            direction = directionList[count % directionLen]
            count += 1
            self.move(direction, 0.3)
            locations = Screen.match(self.target)
            self.__updateRoleLocation(locations)

    # 通过移动角色，刷新角色位置，从而检测到原本场景外的事物
    # TODO：初始水平方向选择要优化，并且方向要保留
    def refreshRoleLocation(self):
        # 如果没有角色位置，即角色标识被遮挡
        if not self.point:
            self.__lookForRole()
            return
        count = self.__refreshRoleLocationCount

        # 每完成一次小循环，执行一次 ScreenStream 的所有匹配器
        microCycleCount = 2
        # 每完成一次中循环，切换在竖直方向上的移动，即 Down 切换成 Up
        mediumCycleCount = 4
        # 每完成一次大循环，切换在水平方向上的移动，即 Right 切换成 Left
        largeCycleCount = 16

        while True:
            hDirection = int(count / largeCycleCount) % 2 == 0 and "Right" or "Left"
            vDirection = int(count / mediumCycleCount) % 2 == 0 and "Down" or "Up"
            direction: Direction = f"{vDirection} {hDirection}"  # type: ignore
            self.move(direction, 0.3)
            count += 1
            self.__refreshRoleLocationCount += 1
            print(f"角色向{direction}移动{count}次")
            if count % microCycleCount == 0:
                break

    def resetRefreshRoleLocationCount(self):
        self.__refreshRoleLocationCount = 0

    def __move(
        self,
        target: Screen.Point,
        offset: Controller.Offset = {"x": 0, "y": 0},
        seconds: float = 0.3,
    ):
        if not self.point:
            return

        x, y = target
        roleX, roleY = self.point

        # print("move 偏移", offset)

        hDirection = ""
        vDirection = ""

        if abs(x - roleX) > offset["x"]:
            hDirection = "Right" if x > roleX else "Left"

        if abs(y - roleY) > offset["y"]:
            vDirection = "Down" if y > roleY else "Up"

        if hDirection or vDirection:
            direction = f"{vDirection} {hDirection}".strip()
            print("move 方向", direction)
            self.move(direction, seconds)  # type: ignore
        else:
            return True

    def __getDistance(self, point: Screen.Point):
        rolePoint = self.getPoint()
        roleX, roleY = rolePoint
        x, y = point

        return abs(x - roleX) + abs(y - roleY)

    def __getNearestPoint(self, points: list[Screen.Point]):
        if not points:
            return

        nearestPoint = points[0]
        distance = self.__getDistance(nearestPoint)

        for point in points:
            d = self.__getDistance(point)
            if d < distance:
                distance = d
                nearestPoint = point

        return nearestPoint

    def attack(
        self,
        monsterList: list[Screen.Point],
        offset: Controller.Offset = {"x": 0, "y": 0},
    ):
        rolePoint = self.getPoint()

        point = self.__getNearestPoint(monsterList)

        if not point:
            return

        print("怪物位置", point)

        if self.__move(point, offset):
            monsterX = point[0]
            roleX = rolePoint[0]

            if monsterX > roleX:
                Controller.press("Right", 0.01)
            else:
                Controller.press("Left", 0.01)

            if self.__skillAttack() == 0:
                self.__defaultAttack()

    def pickUp(self, dropList: list[Screen.Point]):
        point = self.__getNearestPoint(dropList)

        if not point:
            return

        print("掉落位置", point)
        self.__move(point, {"x": 10, "y": 10}, 0.2)

    def checkLock(self) -> bool:
        if not self.point:
            return False

        if not self.prevPoint:
            return False

        x, y = self.point
        prevX, prevY = self.prevPoint

        return x == prevX and y == prevY

    # 普通攻击
    def __defaultAttack(self):
        count = 0
        while count < 5:
            count += 1
            Controller.press("X", 0.1)

    # 技能攻击
    def __skillAttack(self) -> int:
        count = 0

        for skill in self.__skillList:
            if (time.time() - skill["dispatch"]) > skill["CD"]:
                skill["dispatch"] = time.time()
                Controller.press(skill["key"], skill["duration"])
                count += 1
                break

        return count

    def ticketAttack(self):
        Controller.press(self.__ticket["key"], self.__ticket["duration"])

    def buff(self):
        # 旅人
        # Controller.press("Up Space")

        # 奶妈
        Controller.press("Right Space")
        Controller.press("Up Space")
        Controller.press("Down Space")


if __name__ == "__main__":
    # 初始化
    time.sleep(3)
    Controller.setup()
    role = Role("images/roles/3.png")
    # role.refreshRoleLocation()
    # role.refreshRoleLocation()
    ScreenStream.listen()
    ScreenStream.stop()
    Controller.close()
    # role.getRoleLocation()
    # role.move()
