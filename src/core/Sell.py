import time
from services import Controller
from services.Screen import Point


def backCelia():
    Controller.clickImg("images/backCelia.png")
    Controller.press("Space")
    time.sleep(2)


def openStore(point: Point | None = None):
    if not point:
        return
    Controller.click(point)
    time.sleep(1)
    Controller.click(point, {"x": 28, "y": 50})
    time.sleep(1)
    sell()


def sell():
    Controller.press("A")
    Controller.press("Space")
    Controller.press("Left", 0.1)
    Controller.press("Space")
    Controller.press("Esc", 0.2)
    Controller.press("Esc", 0.2)


if __name__ == "__main__":
    Controller.setup()
    openStore()
    Controller.close()
