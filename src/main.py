from operator import eq
import time
from core import Roles_local, SelectRole
from core.Dungeon import Dungeon
from services import Controller, ScreenStream
from core.City import City


roleIndex = 3
while True:
    Controller.setup()
    roleIndex = SelectRole.selectRole(roleIndex)
    print(roleIndex)

    if roleIndex == -1:
        print("关闭")
        Controller.close()
        break

    time.sleep(3)
    roleOption = Roles_local.roleList[roleIndex - 1]
    city = City()
    dungeon = Dungeon(
        name="Silence",
        area="images/dungeons/1.png",
        target="images/dungeons/mapTarget.png",
        offset={"x": 180, "y": 10},
        roleOption=roleOption,
        direction="Right",
    )
    city.dungeon = dungeon
    ScreenStream.listen()
    Controller.close()


Controller.close()
