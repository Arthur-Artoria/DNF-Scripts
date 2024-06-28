from time import sleep, time
from core import Sell, System
from core.Dungeon import Dungeon
from services import Controller, Screen, ScreenStream


class City:
    dungeon: Dungeon | None = None

    def __init__(self) -> None:
        ScreenStream.addListener(self.matchCity)

    def matchCity(self):
        inCity = ScreenStream.exist("images/city.png")

        if inCity:
            self.time = self.time or time()

            if time() - self.time > 120:
                # 在城镇中超时
                self.escape()
            else:
                self.addListenerList()
        else:
            self.time = None
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

    def matchWeakness(self):
        point = Screen.getFirstPoint(ScreenStream.match("images/weakness.png"))

        if not point:
            return

        Controller.click(point)
        sleep(1)
        Controller.clickImg("images/weaknessConfirm.png")
        sleep(1)

    def dispatchRole(self):
        if not self.dungeon:
            return

        System.closeSystemSetting()

        if self.dungeon.needSwitchRole:
            self.dungeon.backCelia()
        else:
            self.dungeon.into()

    def escape(self):
        ScreenStream.stop()
        ScreenStream.addListener(self.matchCity)
        System.closeSystemSetting()
        ScreenStream.listen()
