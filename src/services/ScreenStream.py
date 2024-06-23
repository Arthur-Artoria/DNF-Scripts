from typing import Callable
import mss
import numpy as np
import cv2 as cv

from services import Screen
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

    with mss.mss() as sct:
        while __listenFlag:
            __shot = np.array(sct.grab(__monitor))  # type: ignore
            __shotGray = cv.cvtColor(__shot, cv.COLOR_BGR2GRAY)  # type: ignore
            __callMatcherList()

            # cv.imshow("DNF", __shot)

            if __close():
                __listenFlag = False
                break


def __close() -> bool:
    key = cv.waitKey(30)
    return key == ord("q")


def __callMatcherList():
    for matcher in __matcherList:
        matcher()


def stop():
    global __listenFlag
    __listenFlag = False


def register(fn: Matcher):
    if fn not in __matcherList:
        # print("注册匹配器: " + str(fn))
        __matcherList.append(fn)


def unregister(fn: Matcher):
    if fn in __matcherList:
        # print("注销匹配器: " + str(fn))
        __matcherList.remove(fn)


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
