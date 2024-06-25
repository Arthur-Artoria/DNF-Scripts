from typing import Callable
from src.core import Sell
from src.core.Role import Role
from src.core.Room import Room
from src.services import Controller, ScreenStream


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
        existStore = ScreenStream.exist("images/sell/sellTarget.png")

        if not existStore:
            return

        self.handleStore()
        self.pickUpDrops()

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
        ScreenStream.removeListener(self.matchBoss)
        ScreenStream.removeListener(self.matchReward)
        ScreenStream.removeListener(self.onPickUpEnd)
