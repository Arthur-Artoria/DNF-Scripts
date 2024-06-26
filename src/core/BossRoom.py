from typing import Callable
from core import Roles_local, Sell
from core.Role import Role
from core.Room import Room
from services import Controller, ScreenStream


class BossRoom(Room):
    BOSS_TARGET = "images/dungeons/boss.png"

    def __init__(
        self,
        id: str,
        role: Role,
        onPickUpEnd: Callable,
        sell: bool = False,
    ):
        super().__init__(id, role)
        self.sell = sell
        self.onPickUpEnd = onPickUpEnd
        ScreenStream.addListener(self.matchBoss)

    def matchBoss(self):
        exitBoss = ScreenStream.exist(self.BOSS_TARGET)

        if not exitBoss:
            return

        self.role.ticketAttack()
        return ScreenStream.addListener(self.matchReward)

    def matchReward(self):
        print("开始匹配奖励")
        existReenter = ScreenStream.exist("images/dungeons/reenter.png")

        if not existReenter:
            return

        print("匹配到奖励")

        self.handleStore()
        self.pickUpDrops()

        self.role.move("Up", 1)

        return ScreenStream.addListener(self.onPickUpEnd)

    def handleStore(self):
        if self.sell:
            Sell.sell()
        else:
            # 关闭商店
            Controller.press("Esc", 0.2)

    def pickUpDrops(self):
        # 聚物
        Controller.press("Delete", 0.2)
        # 拾取奖励
        Controller.press("X", 3)

    def destroy(self):
        super().destroy()
        print("Boss房间 销毁")
        ScreenStream.removeListener(self.matchBoss)
        ScreenStream.removeListener(self.matchReward)
        ScreenStream.removeListener(self.onPickUpEnd)
