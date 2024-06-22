from re import X
from time import sleep
from typing import Literal
from services import Controller


class Dungeon:
    def __init__(
        self,
        name: str,
        area: str,
        target: str,
        offset: Controller.Offset | None,
        direction: Literal["Left", "Right"] = "Right",
    ):
        self.name = name
        self.area = area
        self.target = target
        self.offset = offset
        self.direction = direction

    def into(self):
        self.__openMap()
        self.__transport()

    def __openMap(self):
        # 打开工会
        Controller.press(";")
        # 点击传送
        Controller.clickImg("images/transport.png")
        # 同意打开地图
        Controller.press("Space")
        # 点击世界地图
        Controller.clickImg("images/mapSelector.png")

    def __transport(self):
        # 点击目标区域
        Controller.clickImg(self.area)
        # 点击目的地
        Controller.clickImg(self.target, self.offset)
        # 同意传送
        Controller.press("Space")
        # 走向地下城
        Controller.press(self.direction, 3)


if __name__ == "__main__":
    sleep(3)
    Controller.setup()
    dungeon = Dungeon(
        name="Silence",
        area="images/dungeons/1.png",
        target="images/dungeons/target.png",
        offset={"x": 50, "y": 50},
        direction="Right",
    )
    dungeon.into()
    Controller.close()
