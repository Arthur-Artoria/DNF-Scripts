from collections.abc import Callable
from typing import Any
import mss
import mss.models
import mss.screenshot
import mss.tools
import numpy as np
import cv2 as cv

type Matcher = Callable[[], Any]


__shot: mss.screenshot.ScreenShot
__shotArray: np.ndarray
__monitor = {"top": 0, "left": 0, "width": 800, "height": 600}
__matcherList: list[Matcher] = []


def setup():
    with mss.mss() as sct:
        while True:

            __getScreen(sct)
            __callMatcherList()

            if __close():
                break


def __getScreen(sct):
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
        matcher()


def __matchTemplate(shot: cv.typing.MatLike, target: cv.typing.MatLike):
    res = cv.matchTemplate(shot, target, cv.TM_CCOEFF_NORMED)
    locations = np.where(res >= 0.8)
    return locations


def match(imgPath: str):
    shotGray = cv.cvtColor(__shotArray, cv.COLOR_BGR2GRAY)
    target = cv.cvtColor(cv.imread(imgPath), cv.COLOR_BGR2GRAY)
    return __matchTemplate(shotGray, target)
