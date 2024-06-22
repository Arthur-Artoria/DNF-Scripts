import os
import sys
from time import sleep

currentPath = os.path.dirname(os.path.realpath(__file__))
parentPath = os.path.dirname(currentPath)

sys.path.append(parentPath)
sys.path.append("src/services/")

from services import Controller

__BASE_PATH = "images/roles"
__roleList: list[str] = []
__roleIndex: int = 0


def __getRoleList():
    global __roleList
    __roleList = list(
        map(lambda path: __BASE_PATH + "/" + path, os.listdir(__BASE_PATH))
    )


# TODO: 添加 开始游戏 的截图
def __startGame():
    Controller.clickImg("images/start.png")


def selectRole():
    global __roleIndex
    if not __roleList:
        __getRoleList()

    role = __roleList[__roleIndex]
    Controller.clickImg(role)
    __roleIndex += 1
    # __startGame()
    return role


if __name__ == "__main__":
    sleep(3)
    Controller.setup()
    selectRole()
    Controller.press("SP")
    Controller.close()
