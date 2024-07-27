import ScreenStream
from services import Logger


class Scene:
    def __init__(self, name: str, target: str):
        self.name = name
        self.target = target
        ScreenStream.addListener(self.match)

    def match(self):
        locations = ScreenStream.match(self.target)
        for location in zip(*locations[::-1]):
            Logger.log("目标命中:", self.name, "在屏幕坐标:", location)

    def action(self):
        pass


if __name__ == "__main__":
    # 测试
    scene = Scene("test", "images/target.png")
