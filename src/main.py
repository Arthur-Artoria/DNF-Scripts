from operator import eq
import os
import time
from core import Roles_local, SelectRole
from core.Dungeon import Dungeon
from services import Controller, ScreenStream
from core.City import City


def main():
    roleIndex = 0
    while True:
        Controller.setup()
        roleIndex = SelectRole.selectRole(roleIndex)
        print(f"第 {roleIndex} 个角色")

        if roleIndex == -1:
            print("关闭")
            Controller.close()
            os.system("shutdown -s -t  10 ")
            break
        time.sleep(3)
        roleOption = Roles_local.roleList[roleIndex - 1]
        city = City()
        dungeon = Dungeon(
            name="Silence",
            area="images/dungeons/1.png",
            target="images/dungeons/mapTarget.png",
            offset={"x": 200, "y": 10},
            roleOption=roleOption,
            direction="Right",
        )
        city.dungeon = dungeon
        ScreenStream.listen()
        ScreenStream.stop()
        Controller.close()


if __name__ == "__main__":
    try:
        main()
    except:
        Controller.release()
        Controller.close()
        print("程序异常退出")
