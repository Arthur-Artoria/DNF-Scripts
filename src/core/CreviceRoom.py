from core.Room import Room
from services import Screen, ScreenStream


class CreviceRoom(Room):

    __CREVICE_TARGET = "images/dungeons/crevice.png"

    # 检查房间是否已可以同行，即怪物已全部清除
    def matchRoomRelease(self):
        point = Screen.getFirstPoint(ScreenStream.match(self.RELEASE))
        self.__released = point is not None

        if not point:
            point = Screen.getFirstPoint(ScreenStream.match(self.DOOR))
            self.__released = point is not None

        if self.__released:
            ScreenStream.unregister(self.matchMonsterList)
        else:
            ScreenStream.register(self.matchMonsterList)
            ScreenStream.unregister(self.matchDropList)
            ScreenStream.unregister(self.matchCrevice)

    def __unregisterMatcher(self):
        super().__unregisterMatcher()
        ScreenStream.unregister(self.matchCrevice)

    def matchCrevice(self):
        # print("匹配裂缝")
        point = Screen.getFirstPoint(ScreenStream.match(self.__CREVICE_TARGET))

        if not point:
            self.__moveDown()
            return

        cX, cY = point
        roleX, roleY = self.role.getPoint()

        # 在裂缝上面
        if roleY < cY:
            # 与裂缝水平距离很近
            if abs(cX - roleX) < 100:
                if roleX < cX:
                    # 在裂缝左边，向左下移动，远离裂缝
                    self.role.move("Left", 0.2)
                    self.__moveDown()
                else:
                    # 在裂缝右边，向右下移动，远离裂缝
                    self.role.move("Right", 0.2)
                    self.__moveDown()
            else:
                # 与裂缝水平距离较远，直接向下移动
                self.__moveDown()
        else:
            # 在裂缝下面，继续向下移动
            self.__moveDown()

    def __moveDown(self):
        roleX, roleY = self.role.getPoint()

        while abs(roleY - 800) > 20:
            direction = roleY < 800 and "Down" or "Up"
            self.role.move(direction, 0.1)
            self.role.syncSetRoleLocation()
            roleY = self.role.getPoint()[1]

        self.__moveToNextDoor()

    def __moveToNextDoor(self):
        self.role.move("Right", 6)
        self.role.move("Up", 2)
