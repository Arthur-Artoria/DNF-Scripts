import time
from services import Controller


def backCelia():
    Controller.clickImg("images/backCelia.png")
    Controller.press("Space")
    time.sleep(2)


def openStore():
    Controller.clickImg("images/sell/store.png")
    time.sleep(1)
    Controller.clickImg("images/sell/storeMenu.png")
    time.sleep(1)
    sell()


def sell():
    Controller.press("A")
    Controller.press("Space")
    Controller.press("Left")
    Controller.press("Space")
    Controller.press("Esc")


if __name__ == "__main__":
    Controller.setup()
    openStore()
    Controller.close()
