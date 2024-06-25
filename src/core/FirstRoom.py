from core.Role import Direction, Role
from src.core.Room import Room


class FirstRoom(Room):
    def __init__(
        self,
        id: str,
        role: Role,
        nextRoomDirection: Direction,
    ):
        super().__init__(id, role)

        self.role = role
        self.id = id
        self.nextRoomDirection: Direction = nextRoomDirection

        self.enterNextRoom()

    def enterNextRoom(self):
        self.role.move("Right", self.role.firstRoom)
        self.role.move(self.nextRoomDirection, 1.5)
