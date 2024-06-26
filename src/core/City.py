from time import sleep
from core import Sell
from core.Dungeon import Dungeon
from services import Controller, Screen, ScreenStream


class City:
    dungeon: Dungeon | None = None

    def __init__(self) -> None:
        ScreenStream.addListener(self.matchCity)

    def matchCity(self):
        inCity = ScreenStream.exist("images/city.png")

        if inCity:
            self.addListenerList()
        else:
            self.removeListenerList()

    def addListenerList(self):
        ScreenStream.addListener(self.matchWeakness)
        ScreenStream.addListener(self.matchStore)
        ScreenStream.addListener(self.dispatchRole)

    def removeListenerList(self):
        ScreenStream.removeListener(self.matchWeakness)
        ScreenStream.removeListener(self.matchStore)
        ScreenStream.removeListener(self.dispatchRole)

    def matchStore(self):
        storePoint = Screen.getFirstPoint(ScreenStream.match("images/sell/store.png"))

        if not storePoint:
            return

        Sell.openStore(storePoint)

        if self.dungeon:
            self.dungeon.into()

    def matchWeakness(self):
        locations = ScreenStream.match("images/weakness.png")
        point = Screen.getFirstPoint(locations)

        if not point:
            return

        Controller.click(locations)
        sleep(1)
        Controller.clickImg("images/weaknessConfirm.png")
        sleep(1)

        if self.dungeon:
            self.dungeon.moveToDungeonList()

    def dispatchRole(self):
        if not self.dungeon:
            return

        if self.dungeon.needSwitchRole:
            self.dungeon.backCelia()
