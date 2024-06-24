from time import sleep
import time
from typing import Callable
import mss
import numpy as np
import cv2 as cv

from services import Controller, Screen
from constants import Monitor

type Matcher = Callable[[], bool | None]

__listenFlag = True
__shot: np.ndarray | None = None
__shotGray: np.ndarray | None = None
__monitor = Monitor.DNF_MONITOR
__matcherList: list[Matcher] = []


def listen():
    global __shot
    global __shotGray
    global __listenFlag

    __listenFlag = True

    with mss.mss() as sct:
        while __listenFlag:
            __shot = np.array(sct.grab(__monitor))  # type: ignore
            __shotGray = cv.cvtColor(__shot, cv.COLOR_BGR2GRAY)  # type: ignore
            __callMatcherList()

            # cv.imshow("DNF", __shot)  # type: ignore

            if __close():
                __listenFlag = False
                break


def __close() -> bool:
    key = cv.waitKey(30)
    return key == ord("q")


def __callMatcherList():
    global __matcherList

    for matcher in __matcherList:
        if matcher():
            __matcherList.remove(matcher)


def stop():
    global __listenFlag
    clear()
    __listenFlag = False


def register(fn: Matcher):
    if fn not in __matcherList:
        # print("注册匹配器: " + str(fn))
        __matcherList.append(fn)


def unregister(fn: Matcher):
    if fn in __matcherList:
        # print("注销匹配器: " + str(fn))
        __matcherList.remove(fn)


def clear():
    global __matcherList
    __matcherList = []


def match(target: str, area: Screen.Rect | None = None):
    if __shotGray is None:
        # TODO: 抛出异常
        print("[ScreenStream] 截图未初始化")
        return ()
    return Screen.match(target, __shotGray, area)


def exist(target: str, area: Screen.Rect | None = None) -> bool:
    if __shotGray is None:
        # TODO: 抛出异常
        print("[ScreenStream] 截图未初始化")
        return False
    return (
        Screen.getFirstPoint(Screen.match(target, __shotGray, area), area) is not None
    )


def drawRect(point: Screen.Point, color: tuple[int, int, int]):
    if __shot is None:
        return
    cv.rectangle(__shot, point, (point[0] + 20, point[1] + 20), color, 2)


if __name__ == "__main__":
    Controller.setup()
    start = time.time()

    def matcher():
        if time.time() - start > 5:
            print("超时")
            # unregister(matcher)
            # register(__backCity)
            __backCity()

    def __backCity():
        print("返回城镇")

        Controller.press("Esc")

        sleep(1)

        Controller.clickImg("images/city.png")

        sleep(1)

        Controller.clickImg("images/confirm.png")

        # locations = match("images/city.png")
        # point = Screen.getFirstPoint(locations)

        # print("城镇坐标", point)

        # if point:
        #     Controller.click(locations)
        #     sleep(1)
        #     locations = Screen.match("images/cityConfirm.png")
        #     point = Screen.getFirstPoint(locations)

        #     print("确认返回城镇坐标", point)

        #     if point:
        #         print("确认返回城镇")
        #         Controller.click(locations)
        #         sleep(1)
        #     else:
        #         print("未找到确认返回城镇")
        # else:
        #     print("未找到城镇")

    register(matcher)

    listen()

    stop()

    # print(match("images/city.png"))

    Controller.close()
