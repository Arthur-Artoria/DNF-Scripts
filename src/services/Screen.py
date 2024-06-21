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

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

__monitor = {"top": 0, "left": 0, "width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
__matcherList: list[Matcher] = []


def updateMonitorSize(width: int, height: int):
    global __monitor
    __monitor["width"] = width
    __monitor["height"] = height


def __getScreen():
    with mss.mss() as sct:
        return np.array(sct.grab(__monitor))


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
    shot = __getScreen()
    shotGray = cv.cvtColor(shot, cv.COLOR_BGR2GRAY)
    target = cv.cvtColor(cv.imread(imgPath), cv.COLOR_BGR2GRAY)
    return __matchTemplate(shotGray, target)
