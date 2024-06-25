from collections.abc import Callable
from typing import Any
import mss
import mss.base
import mss.models
import mss.screenshot
import mss.tools
import numpy as np
from numpy._typing import NDArray
import cv2 as cv
from constants import Monitor

type Point = tuple[int, int]
type Locations = tuple[NDArray[np.intp], ...]
type Rect = tuple[int, int, int, int]

__monitor = Monitor.SCREEN_MONITOR


def updateMonitor(monitor: Monitor.Monitor):
    global __monitor
    __monitor = monitor


def __getScreen(color: int = cv.COLOR_BGR2GRAY):
    with mss.mss() as sct:
        return cv.cvtColor(np.array(sct.grab(__monitor)), color)  # type: ignore


def __matchTemplate(shotGray: cv.typing.MatLike, target: cv.typing.MatLike):
    res = cv.matchTemplate(shotGray, target, cv.TM_CCOEFF_NORMED)
    locations = np.where(res >= 0.8)
    return locations


def match(
    imgPath: str,
    shotGray=None,
    area: Rect | None = None,
    color: int = cv.COLOR_BGR2GRAY,
):
    if shotGray is None:
        shotGray = __getScreen(color)

    if area is not None:
        shotGray = shotGray[area[1] : area[3], area[0] : area[2]]

    target = cv.cvtColor(cv.imread(imgPath), color)
    return __matchTemplate(shotGray, target)


def matchListAny(
    imgPaths: list[str],
    shotGray=None,
    area: Rect | None = None,
    color: int = cv.COLOR_BGR2GRAY,
):
    if shotGray is None:
        shotGray = __getScreen(color)

    for imgPath in imgPaths:
        locations = match(imgPath, shotGray, area, color)
        point = getFirstPoint(locations, area)
        if point is not None:
            return (locations, point)


def getFirstPoint(locations: Locations, area: Rect | None = None) -> None | Point:
    for pt in zip(*locations[::-1]):
        x, y = int(pt[0]), int(pt[1])
        if area is not None:
            x, y = x + area[0], y + area[1]
        return x, y


def exist(
    target: str,
    area: Rect | None = None,
    color: int = cv.COLOR_BGR2GRAY,
) -> bool:
    return (
        getFirstPoint(
            match(target, None, area, color),
            area,
        )
        is not None
    )
