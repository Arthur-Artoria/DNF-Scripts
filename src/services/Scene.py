from typing import Callable, Self
from services import Screen, ScreenStream

type SceneType = Scene


class Scene:
    def __init__(
        self,
        name: str,
        target: str,
        onMatched: Callable | None = None,
        onNotMatched: Callable | None = None,
        maxMatchCount: int = 3,
    ):
        self.name = name
        self.target = target
        self.onMatched = onMatched
        self.onNotMatched = onNotMatched
        self.maxMatchCount = maxMatchCount

        self.time = None
        self.exist = False
        self.limited = True
        self.matchCount = 0
        self.childScenes: list[Scene] = []
        self.prevScene: Scene | None = None
        self.nextScene: Scene | None = None
        self.point: Screen.Point | None = None
        self.locations: Screen.Locations | None = None

    def addChildScene(self, scene: SceneType):
        self.childScenes.append(scene)

    def checkLimit(self):
        return self.limited and self.matchCount >= self.maxMatchCount

    def matcher(self):
        if self.checkLimit():
            self.setupNextScene()
            return

        if self.limited:
            self.matchCount += 1

        self.locations = ScreenStream.match(self.target)
        self.point = Screen.getFirstPoint(self.locations)
        self.exist = self.point is not None

        if self.exist:
            self.matchCount = self.maxMatchCount
            self.destroyPrevScene()
            self.setupChildScenes()

            if self.onMatched is not None:
                self.onMatched(self.point, self.locations)

            self.setupNextScene()
        else:
            self.destroyChildScenes()
            if self.onNotMatched is not None:
                self.onNotMatched()

    def setPrevScene(self, scene: Self):
        self.prevScene = scene

    def setNextScene(self, scene: Self):
        self.nextScene = scene

    def setup(self):
        ScreenStream.addListener(self.matcher)

    def destroy(self):
        self.point = None
        self.locations = None
        self.matchCount = 0
        ScreenStream.removeListener(self.matcher)

    def setupNextScene(self):
        if self.nextScene is not None:
            self.nextScene.setup()

    def setupChildScenes(self):
        for scene in self.childScenes:
            scene.setup()

    def destroyPrevScene(self):
        if self.prevScene is not None:
            self.prevScene.destroy()

    def destroyChildScenes(self):
        for scene in self.childScenes:
            scene.destroy()


if __name__ == "__main__":
    # 测试
    pass
    # scene = Scene("test", "images/target.png")
