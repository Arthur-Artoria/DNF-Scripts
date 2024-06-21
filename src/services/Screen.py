from collections.abc import Callable
from typing import Any
import mss
import mss.base
import mss.models
import mss.screenshot
import mss.tools
import numpy as np
import cv2 as cv
import pyautogui

type Matcher = Callable[[], bool | None]

__screenWidth, __screenHeight = pyautogui.size()
__shot: mss.screenshot.ScreenShot
__shotArray: np.ndarray
__monitor = {"top": 0, "left": 0, "width":  __screenWidth , "height": __screenHeight}
__matcherList: list[Matcher] = []

print(__monitor)
def setup():
    with mss.mss() as sct:
        while True:

            __getScreen(sct)
            __callMatcherList()

            if __close():
                break


def updateMonitorSize(width: int, height: int):
    global __monitor
    __monitor["width"] = width
    __monitor["height"] = height
    


def __getScreen(sct: mss.base.MSSBase):
    global __shot
    global __shotArray

    __shot = sct.grab(__monitor)
    __shotArray = np.array(__shot)


def __close() -> bool:
    key = cv.waitKey(10)
    return key == ord("q")


def register(fn: Matcher):
    __matcherList.append(fn)


def __callMatcherList():
    for matcher in __matcherList:
        isRemove = matcher()
        if isRemove:
            __matcherList.remove(matcher)


def __matchTemplate(shot: cv.typing.MatLike, target: cv.typing.MatLike):
    res = cv.matchTemplate(shot, target, cv.TM_CCOEFF_NORMED)
    locations = np.where(res >= 0.8)
    return locations


def match(imgPath: str):
    shotGray = cv.cvtColor(__shotArray, cv.COLOR_BGR2GRAY)
    target = cv.cvtColor(cv.imread(imgPath), cv.COLOR_BGR2GRAY)
    return __matchTemplate(shotGray, target)
