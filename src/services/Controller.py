import time
from multiprocessing import Process, Queue

from services import Screen, Serial
from constants import Keyboard


queue: Queue = Queue()
serialProcess: Process


def setup(sleep: bool = True):
    global serialProcess
    if sleep:
        time.sleep(3)

    # Serial.setup()
    serialProcess = Process(target=Serial.worker, args=(queue,))
    serialProcess.start()


def close():
    queue.put(None)
    serialProcess.terminate()


def press(key: str, seconds: float = 0.5, sleep: float = 0.5):
    # if key == None:
    #     time.sleep(0.5)
    #     return
    data = "".join(map(lambda x: Keyboard.options[x]["key"], key.split(" ")))
    queue.put((Serial.INSTRUCTION_PRESS, data, None))


def release():
    queue.put((Serial.INSTRUCTION_RELEASE, None, None))


def click(point: Screen.Point | None, offset: Serial.Offset | None = None):
    queue.put((Serial.INSTRUCTION_CLICK, point, offset))


def mouseMove(x: int, y: int):
    point = (x, y)
    queue.put((Serial.INSTRUCTION_MOUSE_MOVE, point, None))


def clickImg(imgPath: str, offset: Serial.Offset | None = None):
    point = Screen.getFirstPoint(Screen.match(imgPath))
    click(point, offset)


if __name__ == "__main__":
    setup(False)
    # press("Up")
    close()
