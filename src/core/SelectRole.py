import os
import sys
import time

from services import Controller

__BASE_PATH = "images/roles"
__roleList: list[str] = []
__roleIndex: int = 0


def __getRoleList():
    global __roleList
    __roleList = list(
        map(lambda path: __BASE_PATH + "/" + path, os.listdir(__BASE_PATH))
    )


def __startGame():
    Controller.clickImg("images/start.png")


def toSelectRole():
    Controller.press("Esc")
    Controller.clickImg("images/selectRole.png")
    time.sleep(2)


def selectRole(index=__roleIndex) -> bool | int:
    global __roleIndex
    if not __roleList:
        __getRoleList()

    if index > len(__roleList):
        return False

    role = __roleList[index]
    Controller.clickImg(role)
    __roleIndex = index + 1
    Controller.press("Space")
    return index


if __name__ == "__main__":
    time.sleep(3)
    Controller.setup()
    selectRole()
    Controller.close()
