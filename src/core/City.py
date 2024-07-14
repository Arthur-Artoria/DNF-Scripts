from time import sleep, time
from core import Roles_local, Sell, System
from core.Dungeon import Dungeon
from services import Controller, Screen, ScreenStream
from services.Scene import Scene


class City(Scene):
    TARGET = "images/city.png"

    def __init__(self, dungeon: Dungeon) -> None:
        super().__init__("城镇", self.TARGET)
        self.limited = False
        self.dungeon = dungeon

        self.closeScene = self.createCloseScene()
        self.storeScene = self.createStoreScene()
        self.weaknessScene = self.createWeaknessScene()
        self.roleEndScene = self.createRoleEndScene()

        self.weaknessScene.setNextScene(self.roleEndScene)

        self.addChildScene(self.closeScene)
        self.addChildScene(self.storeScene)
        self.addChildScene(self.weaknessScene)

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

    def handleCloseMatched(self, point: Screen.Point, locations):
        Controller.click(point)

    def handleWeaknessMatched(self, point: Screen.Point, locations):
        Controller.click(point)
        sleep(1)
        Controller.clickImg("images/weaknessConfirm.png")
        sleep(1)

    def handleStoreMatched(self, point: Screen.Point, locations):
        Sell.openStore(point)

    def handleRoleEndMatched(self, point: Screen.Point, locations):
        self.dungeon.backCelia()

    def handleRoleEndNotMatched(self):
        self.dungeon.into()

    def destroyChildScenes(self):
        super().destroyChildScenes()
        self.roleEndScene.destroy()

    def escape(self):
        ScreenStream.stop()
        ScreenStream.addListener(self.matcher)
        System.closeSystemSetting()
        ScreenStream.listen()


if __name__ == "__main__":
    Controller.setup()

    roleOption = Roles_local.roleList[0]
    dungeon = Dungeon(
        name="Silence",
        area="images/dungeons/1.png",
        target="images/dungeons/mapTarget.png",
        offset=(200, 10),
        roleOption=roleOption,
        direction="Right",
    )

    city = City(dungeon)
    city.setup()
    ScreenStream.listen()
    ScreenStream.stop()
    Controller.close()
