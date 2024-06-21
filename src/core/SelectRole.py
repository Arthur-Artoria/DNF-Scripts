import os
from services import Controller


__BASE_PATH = "images/roles"
__roleList: list[str] = []
__roleIndex: int = 0


# TODO：添加 角色名称 的截图
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
    __startGame()
    return role


if __name__ == "__main__":
    print(__getRoleList())
