from time import sleep
from services import Controller, Screen


def openSystemSetting():
    existSystemSetting = False

    while not existSystemSetting:
        Controller.press("Esc", 0.1, 1)
        Controller.mouseMove(10, 1000)
        existSystemSetting = Screen.exist("images/settings.png")
        sleep(1)


def closeSystemSetting():
    openSystemSetting()
    Controller.press("Esc", 0.1, 1)
