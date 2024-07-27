from time import sleep
import win32gui

from services import Logger, Screen
from services import Controller

__handler: int
__rect: tuple[int, int, int, int]


def setWindow():
    Controller.setup()
    __getWindow()
    __openController()
    __setWindowSize()
    __moveWindow()
    Controller.close()


def __getWindow():
    global __handler
    __handler = win32gui.FindWindow(None, "地下城与勇士：创新世纪")
    win32gui.SetForegroundWindow(__handler)


def __openController():
    sleep(1)
    Controller.press("EC")


def __setWindowSize():
    global __rect

    locations = Screen.match("images/settings.png")
    Logger.log(locations)
    # TODO：通过游戏菜单调整游戏窗口大小
    __rect = win32gui.GetWindowRect(__handler)


def __moveWindow():
    left, top, right, bottom = __rect
    width = right - left
    height = bottom - top
    # TODO: DNF 禁止 MoveWindow 操作，需要使用鼠标模拟拖拽来移动窗口
    # win32gui.MoveWindow(__handler, -8, -1, width, height, True)


if __name__ == "__main__":
    setWindow()
