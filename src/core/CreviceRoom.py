from core.Room import Room
from services import Screen, ScreenStream


class CreviceRoom(Room):

    __CREVICE_TARGET = "images/dungeons/crevice.png"

    # 检查房间是否已可以同行，即怪物已全部清除
    def __matchRoomRelease(self):
        point = Screen.getFirstPoint(ScreenStream.match(self.__RELEASE))
        self.__released = point is not None

        if not point:
            point = Screen.getFirstPoint(ScreenStream.match(self.__DOOR))
            self.__released = point is not None

        if self.__released:
            ScreenStream.register(self.__matchCrevice)
            ScreenStream.unregister(self.__matchMonsterList)
        else:
            ScreenStream.register(self.__matchMonsterList)
            ScreenStream.unregister(self.__matchDropList)
            ScreenStream.unregister(self.__matchCrevice)

    def __unregisterMatcher(self):
        super().__unregisterMatcher()
        ScreenStream.unregister(self.__matchCrevice)

    def __matchCrevice(self):
        point = Screen.getFirstPoint(ScreenStream.match(self.__CREVICE_TARGET))

        if not point:
            return

        cX, cY = point
        roleX, roleY = self.__role.getPoint()

        # 在裂缝上面
        if roleY < cY:
            # 与裂缝水平距离很近
            if abs(cX - roleX) < 100:
                if roleX < cX:
                    # 在裂缝左边，向左下移动，远离裂缝
                    self.__role.move("Left", 0.2)
                    self.__moveDown()
                else:
                    # 在裂缝右边，向右下移动，远离裂缝
                    self.__role.move("Right", 0.2)
                    self.__moveDown()
            else:
                # 与裂缝水平距离较远，直接向下移动
                self.__moveDown()
        else:
            # 在裂缝下面，继续向下移动
            self.__moveDown()

    def __moveDown(self):
        roleX, roleY = self.__role.getPoint()

        while abs(roleY - 800) > 20:
            direction = roleY < 800 and "Down" or "Up"
            self.__role.move(direction, 0.1)
            self.__role.syncSetRoleLocation()

        self.__moveToNextDoor()

    def __moveToNextDoor(self):
        self.__role.move("Right", 6)
        self.__role.move("Up", 2)
