from typing import Callable
from core.MonsterRoom import MonsterRoom
from services import Screen, ScreenStream
from core.Role import Direction, Role


class CreviceRoom(MonsterRoom):
    def __init__(
        self, id: str, role: Role, nextRoomDirection: Direction, onLeaved: Callable
    ):
        super().__init__(id, role, nextRoomDirection)
        self.onLeaved = onLeaved

    # 检查房间是否已可以同行，即怪物已全部清除
    def matchRoomRelease(self):
        point = Screen.getFirstPoint(ScreenStream.match(self.RELEASE))
        self.released = point is not None

        if not point:
            point = Screen.getFirstPoint(ScreenStream.match(self.DOOR))
            self.released = point is not None

        if not self.released:
            ScreenStream.addListener(self.matchMonsterList)
            return

        return ScreenStream.addListener(self.adjustRoleLocation)

    def adjustRoleLocation(self):
        roleX, roleY = self.role.getPoint()

        if abs(roleY - 800) > 20:
            direction = roleY < 800 and "Down" or "Up"
            self.role.move(direction, 0.1)
        else:
            self.moveToNextRoom()
            return True

    def moveToNextRoom(self):
        self.role.move("Right", 6)
        self.role.move("Up", 2)
        self.onLeaved()
