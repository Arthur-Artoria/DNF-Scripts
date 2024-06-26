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
    Controller.clickImg("images/sell/storeMenu.png")
    time.sleep(1)
    sell()


def sell():
    Controller.press("A")
    Controller.press("Space")
    Controller.press("Left", 0.1)
    Controller.press("Space")
    Controller.press("Esc")


if __name__ == "__main__":
    Controller.setup()
    openStore()
    Controller.close()
