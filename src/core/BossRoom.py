import os
from threading import Thread
from typing import Callable
from constants.DNFConfig_local import COLLECT
from core import Roles_local, Sell
from core.Role import Role
from core.Room import Room
from services import Controller, Logger, ScreenStream


class BossRoom(Room):
    BOSS_TARGET = "images/dungeons/boss.png"
    BOSS_BASE_PATH = "images/dungeons/boss/"

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
        self.bossList: list[str] = []
        self.bossThreadList: list[Thread] = []

        self.initBossList()
        ScreenStream.addListener(self.matchBossList)
        Logger.log("Boss房间 初始化")

    def initBossList(self):
        self.bossList = list(
            map(
                lambda path: self.BOSS_BASE_PATH + path,
                os.listdir(self.BOSS_BASE_PATH),
            )
        )

    def matchBossList(self):
        self.bossThreadList = []

        for boss in self.bossList:
            exitBoss = ScreenStream.exist(boss)

            if exitBoss:
                Logger.log("匹配到Boss", boss)
                self.role.ticketAttack()
                ScreenStream.addListener(self.matchReward)

    def matchReward(self):
        existReenter = ScreenStream.exist("images/dungeons/reenter.png")

        if not existReenter:
            return

        Logger.log("匹配到奖励")
        ScreenStream.removeListener(self.matchBossList)

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
        Controller.press(COLLECT, 0.2)
        # 拾取奖励
        Controller.press("X", 3)

    def destroy(self):
        super().destroy()
        Logger.log("Boss房间 销毁")
        ScreenStream.removeListener(self.matchBossList)
        ScreenStream.removeListener(self.matchReward)
        ScreenStream.removeListener(self.onPickUpEnd)
