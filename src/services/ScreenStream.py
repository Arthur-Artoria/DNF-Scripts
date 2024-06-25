from time import sleep
import time
from typing import Callable
import mss
import numpy as np
import cv2 as cv

from services import Controller, Screen
from constants import Monitor

type Listener = Callable[[], bool | None]

__listenFlag = True
__shot: np.ndarray | None = None
__shotGray: np.ndarray | None = None
__monitor = Monitor.DNF_MONITOR
__listenerList: list[Listener] = []


def listen():
    global __shot
    global __shotGray
    global __listenFlag

    __listenFlag = True

    with mss.mss() as sct:
        while __listenFlag:
            __shot = np.array(sct.grab(__monitor))  # type: ignore
            __shotGray = cv.cvtColor(__shot, cv.COLOR_BGR2GRAY)  # type: ignore
            __dispatchListenerList()

            # cv.imshow("DNF", __shot)  # type: ignore

            if __close():
                __listenFlag = False
                break


def __close() -> bool:
    key = cv.waitKey(30)
    return key == ord("q")


def __dispatchListenerList():
    global __listenerList
    for matcher in __listenerList:
        if matcher():
            __listenerList.remove(matcher)


def stop():
    global __listenFlag
    clear()
    __listenFlag = False


def addListener(fn: Listener) -> bool:
    if fn not in __listenerList:
        __listenerList.append(fn)

    return True


def removeListener(fn: Listener):
    if fn in __listenerList:
        __listenerList.remove(fn)


def clear():
    global __listenerList
    __listenerList = []


def match(
    target: str,
    area: Screen.Rect | None = None,
    color: int = cv.COLOR_BGR2GRAY,
):
    if __shotGray is None:
        # TODO: 抛出异常
        print("[ScreenStream] 截图未初始化")
        return ()
    return Screen.match(target, __shotGray, area, color)


def exist(
    target: str,
    area: Screen.Rect | None = None,
    color: int = cv.COLOR_BGR2GRAY,
) -> bool:
    if __shotGray is None:
        # TODO: 抛出异常
        print("[ScreenStream] 截图未初始化")
        return False
    return (
        Screen.getFirstPoint(Screen.match(target, __shotGray, area, color), area)
        is not None
    )


def drawRect(point: Screen.Point, color: tuple[int, int, int]):
    if __shot is None:
        return
    cv.rectangle(__shot, point, (point[0] + 20, point[1] + 20), color, 2)


def matchListAny(targetList: list[str], area: Screen.Rect | None = None):
    return Screen.matchListAny(targetList, __shotGray, area)
