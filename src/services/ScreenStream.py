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
__shot: np.ndarray
__shotGray: np.ndarray
__monitor = Monitor.DNF_MONITOR
__listenerList: list[Listener] = []


def listen():
    global __shot
    global __shotGray
    global __listenFlag

    print("启动监听器")
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

    # print("监听器触发", len(__listenerList), __listenerList)

    for matcher in __listenerList:
        if not __listenFlag:
            return

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


def getShot(color: int = cv.COLOR_BGR2GRAY) -> np.ndarray:
    if color == cv.COLOR_BGR2GRAY:
        return __shotGray
    else:
        return cv.cvtColor(__shot, color)


def match(
    target: str,
    area: Screen.Rect | None = None,
    color: int = cv.COLOR_BGR2GRAY,
):
    return Screen.match(target, getShot(color), area, color)


def exist(
    target: str,
    area: Screen.Rect | None = None,
    color: int = cv.COLOR_BGR2GRAY,
) -> bool:
    return (
        Screen.getFirstPoint(Screen.match(target, getShot(color), area, color), area)
        is not None
    )


def drawRect(point: Screen.Point, color: tuple[int, int, int]):
    if __shot is None:
        return
    cv.rectangle(__shot, point, (point[0] + 20, point[1] + 20), color, 2)


def matchListAny(targetList: list[str], area: Screen.Rect | None = None):
    return Screen.matchListAny(targetList, __shotGray, area)


if __name__ == "__main__":
    sleep(2)

    def matcher():
        point = Screen.getFirstPoint(match("images/dungeons/roleEnd.png"))
        print(point)

    addListener(matcher)

    license()
