from typing import Callable, Self
import ScreenStream
from services import Screen

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
        self.matchCount = 0
        self.childrenScenes: list[Scene] = []
        self.prevScene: Scene | None = None
        self.nextScene: Scene | None = None
        self.point: Screen.Point | None = None
        self.locations: Screen.Locations | None = None

    def addChildScene(self, scene: SceneType):
        self.childrenScenes.append(scene)

    def getStatus(self):
        return self.matchCount >= self.maxMatchCount

    def matcher(self):
        if self.getStatus():
            self.setupNextScene()
            return

        self.matchCount += 1
        self.locations = ScreenStream.match(self.target)
        self.point = Screen.getFirstPoint(self.locations)
        self.exist = self.point is not None

        if self.exist:
            self.matchCount = self.maxMatchCount
            self.destroyPrevScene()
            self.setupChildrenScenes()

            if self.onMatched is not None:
                self.onMatched(self.point, self.locations)

            self.setupNextScene()
        else:
            self.destroyChildrenScenes()
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
        self.prevScene = None
        self.nextScene = None
        self.onMatched = None
        self.onNotMatched = None
        ScreenStream.removeListener(self.matcher)

    def setupNextScene(self):
        if self.nextScene is not None:
            self.nextScene.setup()

    def setupChildrenScenes(self):
        map(lambda scene: scene.setup(), self.childrenScenes)

    def destroyPrevScene(self):
        if self.prevScene is not None:
            self.prevScene.destroy()

    def destroyChildrenScenes(self):
        map(lambda scene: scene.destroy(), self.childrenScenes)


if __name__ == "__main__":
    # 测试
    pass
    # scene = Scene("test", "images/target.png")
