from abc import ABC, abstractmethod
import time

from core.Role import Role


class Room:
    def __init__(self, id: str, role: Role):
        self.id = id
        self.role = role
        self.startTime = time.time()

    @abstractmethod
    def matchRoomStatus(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
