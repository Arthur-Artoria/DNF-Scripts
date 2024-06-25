import mss
import pyautogui
import cv2 as cv
import numpy as np

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SCREEN_MONITOR = {
    "top": 0,
    "left": 0,
    "width": SCREEN_WIDTH,
    "height": SCREEN_HEIGHT,
}


def getFirstPoint(locations, area=None):
    for pt in zip(*locations[::-1]):
        x, y = int(pt[0]), int(pt[1])
        if area is not None:
            x, y = x + area[0], y + area[1]
        return x, y


def getScreen():
    with mss.mss() as sct:
        shot = np.array(sct.grab(SCREEN_MONITOR))  # type: ignore
        shot = cv.cvtColor(shot, cv.COLOR_BGR2RGB)
        target = cv.cvtColor(cv.imread("test.png"), cv.COLOR_BGR2RGB)
        res = cv.matchTemplate(shot, target, cv.TM_CCOEFF_NORMED)
        locations = np.where(res >= 0.8)
        print(locations)
        print(getFirstPoint(locations))


getScreen()
