import time
from core import Roles_local, SelectRole
from core.Dungeon import Dungeon
from services import Controller, ScreenStream

time.sleep(3)
Controller.setup()

while True:
    roleIndex = SelectRole.selectRole()

    if roleIndex == False:
        break

    time.sleep(3)
    roleOption = Roles_local.roleList[roleIndex]
    dungeon = Dungeon(
        name="Silence",
        area="images/dungeons/1.png",
        target="images/dungeons/mapTarget.png",
        offset={"x": 20, "y": 20},
        roleOption=roleOption,
        direction="Right",
    )
    dungeon.into()
    ScreenStream.listen()

Controller.close()
