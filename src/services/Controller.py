import time
from multiprocessing import Process, Queue

from services import Screen, Serial
from constants import Keyboard


queue: Queue = Queue()


def setup(sleep: bool = True):
    if sleep:
        time.sleep(3)
    Serial.setup()


def close():
    queue.put(None)


def press(key: str):
    data = "".join(map(lambda x: Keyboard.options[x]["key"], key.split(" ")))
    queue.put((Serial.INSTRUCTION_PRESS, data, None))


def release():
    queue.put((Serial.INSTRUCTION_RELEASE, None, None))


def click(point: Screen.Point | None, offset: Serial.Offset | None = None):
    queue.put((Serial.INSTRUCTION_CLICK, point, offset))


def mouseMove(point: Screen.Point):
    queue.put((Serial.INSTRUCTION_MOUSE_MOVE, point, None))


def clickImg(imgPath: str, offset: Serial.Offset | None = None):
    point = Screen.getFirstPoint(Screen.match(imgPath))
    click(point, offset)


if __name__ == "__main__":
    # setup(False)
    # press("Up")
    # close()

    serialProcess = Process(target=Serial.worker, args=(queue,))
    serialProcess.start()

    press("Up")
    print("11111")
    release()
    click((100, 100))
    mouseMove((100, 100))

    close()

#
