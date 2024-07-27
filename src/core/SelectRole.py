import os
import sys
import time
from typing import Literal

from core import Roles_local, System
from services import Controller, Logger, Screen

__BASE_PATH = "images/roles_local"
__roleList = Roles_local.roleList
__roleIndex: int = 0


def __startGame():
    Controller.clickImg("images/start.png")


def toSelectRole():
    System.openSystemSetting()
    Controller.clickImg("images/selectRole.png")
    time.sleep(2)


def selectRole(index=__roleIndex) -> int:
    global __roleIndex

    if index == len(__roleList):
        return -1

    role = __roleList[index]
    __roleIndex = index + 1

    if "skip" in role and role["skip"] is True:
        Logger.log(role["name"], "跳过")
        return selectRole(__roleIndex)

    target = f"{__BASE_PATH}/{index}.png"

    point = Screen.getFirstPoint(Screen.match(target))

    if point:
        Controller.click(point)
        Controller.press("Space")
    else:
        pageDown()
        return selectRole(index)

    return __roleIndex


def pageDown():
    Controller.click((1187, 800))


def pageUp():
    Controller.click((1187, 510))


if __name__ == "__main__":
    time.sleep(3)
    Controller.setup()
    selectRole()
    Controller.close()
