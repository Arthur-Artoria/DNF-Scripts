from time import sleep, time
from core import Sell, System
from core.Dungeon import Dungeon
from services import Controller, Screen, ScreenStream
from services.Scene import Scene


class City(Scene):
    TARGET = "images/city.png"

    def __init__(self, dungeon: Dungeon) -> None:
        super().__init__("城镇", self.TARGET)
        self.dungeon = dungeon
        self.matchStoreCount = 0
        self.matchWeaknessCount = 0
        # ScreenStream.addListener(self.matcher)

    def matcher(self):
        inCity = ScreenStream.exist(self.TARGET)

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

    def createCloseScene(self) -> Scene:
        name = "关闭按钮"
        target = "images/close.png"
        return Scene(name, target, onMatched=self.handleCloseMatched)

    def createStoreScene(self) -> Scene:
        name = "商店"
        target = "images/sell/store.png"
        return Scene(name, target, onMatched=self.handleStoreMatched)

    def createWeaknessScene(self) -> Scene:
        name = "解除虚弱"
        target = "images/weakness.png"
        return Scene(name, target, onMatched=self.handleWeaknessMatched)

    def createRoleEndScene(self) -> Scene:
        name = "角色疲劳值"
        target = "images/dungeons/roleEnd.png"
        onMatched = self.handleRoleEndMatched
        onNotMatched = self.handleRoleEndNotMatched
        return Scene(name, target, onMatched, onNotMatched)

    def handleCloseMatched(self, point: Screen.Point):
        Controller.click(point)

    def handleWeaknessMatched(self, point: Screen.Point):
        Controller.click(point)
        sleep(1)
        Controller.clickImg("images/weaknessConfirm.png")
        sleep(1)

    def handleStoreMatched(self, point: Screen.Point):
        Sell.openStore(point)

    def handleRoleEndMatched(self, point: Screen.Point):
        self.dungeon.backCelia()

    def handleRoleEndNotMatched(self):
        self.dungeon.into()

    def addListenerList(self):
        ScreenStream.addListener(self.matchClose)
        ScreenStream.addListener(self.matchRoleEnd)
        ScreenStream.addListener(self.matchWeakness)
        ScreenStream.addListener(self.matchStore)
        if self.matchWeaknessCount > 2:
            ScreenStream.addListener(self.dispatchRole)

    def removeListenerList(self):
        self.matchStoreCount = 0
        self.matchWeaknessCount = 0
        ScreenStream.removeListener(self.matchClose)
        ScreenStream.removeListener(self.matchRoleEnd)
        ScreenStream.removeListener(self.matchWeakness)
        ScreenStream.removeListener(self.matchStore)
        ScreenStream.removeListener(self.dispatchRole)

    def matchStore(self):
        if self.matchStoreCount > 3:
            return
        self.matchStoreCount += 1
        storePoint = Screen.getFirstPoint(ScreenStream.match("images/sell/store.png"))

        if not storePoint:
            return

        print("发现商店魔法书", storePoint)

        self.matchStoreCount = 4
        Sell.openStore(storePoint)

    def matchWeakness(self):
        self.matchWeaknessCount += 1
        point = Screen.getFirstPoint(ScreenStream.match("images/weakness.png"))

        if not point:
            return

        self.matchWeaknessCount = 4

        Controller.click(point)
        sleep(1)
        Controller.clickImg("images/weaknessConfirm.png")
        sleep(1)

    def matchClose(self):
        point = Screen.getFirstPoint(ScreenStream.match("images/close.png"))

        if not point:
            return

        Controller.click(point)
        sleep(1)

    def matchRoleEnd(self):
        roleEnd = ScreenStream.exist("images/dungeons/roleEnd.png")

        if not roleEnd:
            return

        if not self.dungeon:
            return

        # print("角色疲劳已用光")
        self.dungeon.backCelia()

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
        ScreenStream.addListener(self.matcher)
        System.closeSystemSetting()
        ScreenStream.listen()
