from ast import While
from random import randint
from time import sleep
import time
from typing import Literal
from services import Controller, Screen, ScreenStream, Serial
from constants import Monitor

type Direction = Literal[
    "Up", "Down", "Left", "Right", "Up Left", "Up Right", "Down Left", "Down Right"
]


class Role:
    __refreshRoleLocationDirectionList: list[Direction] = [
        "Down Right",
        "Up Right",
        "Down Left",
        "Up Left",
    ]
    __refreshRoleLocationCount = 0

    def __init__(self, target: str, options):
        self.target = target
        self.point: Screen.Point | None = None
        self.prevPoint: Screen.Point | None = None
        self.__offset = options["offset"]
        self.__skillList = options["skillList"]
        self.__ticket = options["ticket"]
        self.__buffList = options["buffList"]
        self.speed = options["speed"]
        self.firstRoom = options["firstRoom"]

    def setup(self):
        ScreenStream.addListener(self.setRoleLocation)

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
        # print("上一次角色位置：", self.prevPoint, "当前角色位置：", self.point)

    def setRoleLocation(self):
        locations = ScreenStream.match(self.target)
        # print("匹配角色位置", locations)
        self.__updateRoleLocation(locations)

    def syncSetRoleLocation(self):
        time.sleep(0.5)
        self.__updateRoleLocation(Screen.match(self.target))

    def move(self, direction: Direction, seconds: float = 0.5):
        Controller.press(direction)

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
            # print(f"角色向{direction}移动{count}次")
            if count % microCycleCount == 0:
                break

    def resetRefreshRoleLocationCount(self):
        self.__refreshRoleLocationCount = 0

    def __move(
        self,
        target: Screen.Point,
        offset: Serial.Offset = (0, 0),
        seconds: float = 0.3,
    ):
        if not self.point:
            return

        x, y = target
        roleX, roleY = self.point
        offsetX, offsetY = offset

        # print("move 偏移", offset)

        hDirection = ""
        vDirection = ""

        if abs(x - roleX) > offsetX:
            hDirection = "Right" if x > roleX else "Left"

        if abs(y - roleY) > offsetY:
            vDirection = "Down" if y > roleY else "Up"

        if hDirection or vDirection:
            direction = f"{vDirection} {hDirection}".strip()
            self.move(direction, seconds)  # type: ignore

        if not hDirection or not vDirection:
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
        offset: Serial.Offset = (0, 0),
    ):
        point = self.__getNearestPoint(monsterList)

        if not point:
            return

        print("怪物位置", point)

        if self.__move(point, offset, 0.5):
            self.syncSetRoleLocation()
            rolePoint = self.getPoint()

            monsterX = point[0]
            roleX = rolePoint[0]

            if monsterX > roleX:
                Controller.press("Right")
            else:
                Controller.press("Left")

            if self.skillAttack() == 0:
                self.__defaultAttack()

    def pickUp(self, dropList: list[Screen.Point]):
        point = self.__getNearestPoint(dropList)

        if not point:
            return

        self.__move(point, (10, 10), self.speed)

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
            Controller.press("X")

    # 技能攻击
    def skillAttack(self) -> int:
        count = 0

        for skill in self.__skillList:
            if (time.time() - skill["dispatch"]) > skill["CD"]:
                skill["dispatch"] = time.time()
                Controller.press(skill["key"])
                count += 1
                if count == 1:
                    break

        return count

    def ticketAttack(self):
        Controller.press(self.__ticket["key"])

    def buff(self):
        for buff in self.__buffList:
            Controller.press(buff)


if __name__ == "__main__":
    pass
    # 初始化
    # time.sleep(3)
    # Controller.setup()
    # role = Role("images/roles/3.png")
    # role.refreshRoleLocation()
    # role.refreshRoleLocation()
    # ScreenStream.listen()
    # ScreenStream.stop()
    # Controller.close()
    # role.getRoleLocation()
    # role.move()
