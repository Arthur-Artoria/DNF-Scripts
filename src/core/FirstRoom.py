from core.Role import Direction, Role
from core.Room import Room
from services import Screen, ScreenStream


class FirstRoom(Room):

    def __init__(
        self,
        role: Role,
        row: int,
        col: int,
        nextRoomDirection: Direction,
    ):
        super().__init__(role, row, col, nextRoomDirection)
        ScreenStream.unregister(self.matchRoomRelease)
        ScreenStream.register(self.matchRoomRelease)

    # 检查房间是否已可以同行，即怪物已全部清除
    def matchRoomRelease(self):
        print("First Room")
        point = Screen.getFirstPoint(ScreenStream.match(self.RELEASE))
        self.released = point is not None

        if not point:
            point = Screen.getFirstPoint(ScreenStream.match(self.DOOR))
            self.released = point is not None

        if self.released:
            self.role.move("Right", self.role.firstRoom)
            self.role.move(self.nextRoomDirection, 1.5)
            ScreenStream.unregister(self.matchRoomRelease)
