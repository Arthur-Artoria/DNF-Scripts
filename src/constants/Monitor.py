from typing import Literal
import pyautogui


type Monitor = dict[Literal["top", "left", "width", "height"], int]

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SCREEN_MONITOR: Monitor = {
    "top": 0,
    "left": 0,
    "width": SCREEN_WIDTH,
    "height": SCREEN_HEIGHT,
}
DNF_MONITOR: Monitor = {"top": 0, "left": 0, "width": 400, "height": 400}
