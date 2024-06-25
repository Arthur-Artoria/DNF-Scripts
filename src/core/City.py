from time import sleep
from src.core.Dungeon import Dungeon
from src.services import Controller, Screen, ScreenStream


class City:
    dungeon: Dungeon | None = None

    def matchCity(self):
        inCity = ScreenStream.exist("images/city.png")

        if inCity:
            self.addListenerList()
        else:
            self.removeListenerList()

    def addListenerList(self):
        ScreenStream.addListener(self.matchWeakness)

    def removeListenerList(self):
        ScreenStream.removeListener(self.matchWeakness)

    def matchWeakness(self):
        locations = ScreenStream.match("images/weakness.png")
        point = Screen.getFirstPoint(locations)

        if not point:
            return

        Controller.click(locations)
        sleep(1)
        Controller.clickImg("images/weaknessConfirm.png")
        sleep(1)
        self.dungeon?.moveToDungeonList.()
