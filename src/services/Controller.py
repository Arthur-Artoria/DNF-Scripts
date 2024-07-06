import time
from typing import Literal, Optional
import numpy as np
from numpy._typing import NDArray
import serial
import ch9329Comm
from services import Screen
from constants import Keyboard, Monitor

type Offset = dict[Literal["x", "y"], int]

__mouse: ch9329Comm.mouse.DataComm
__keyboard: ch9329Comm.keyboard.DataComm


def setup(sleep: bool = True):
    if sleep:
        time.sleep(3)
    serial.ser = serial.Serial("COM3", 115200)  # type: ignore # 开启串口
    __initMouse()
    __initKeyboard()
    __extendKeyboard()


def __initKeyboard():
    global __keyboard
    __keyboard = ch9329Comm.keyboard.DataComm()


def __extendKeyboard():
    global __keyboard
    for value in Keyboard.options.values():
        if "code" in value:
            key, code = value.values()
            __keyboard.normal_button_hex_dict[key] = code


def __initMouse():
    global __mouse
    __mouse = ch9329Comm.mouse.DataComm(Monitor.SCREEN_WIDTH, Monitor.SCREEN_HEIGHT)


def close():
    serial.ser.close()  # type: ignore


def press(key: str, seconds: float = 0.5, sleep: float = 0.5):
    if key == None:
        time.sleep(0.5)
        return
    data = "".join(map(lambda x: Keyboard.options[x]["key"], key.split(" ")))
    __keyboard.send_data(data)
    time.sleep(seconds)
    __keyboard.release()
    time.sleep(sleep)


def release():
    __keyboard.release()


def click(
    locations: tuple[NDArray[np.intp], ...] | Screen.Point | None,
    offset: Offset | None = None,
):
    if locations is None:
        return

    x, y = locations

    if isinstance(x, np.ndarray) and isinstance(x, np.ndarray):
        point = Screen.getFirstPoint(locations)  # type: ignore
    else:
        point: Screen.Point = locations  # type: ignore

    offsetX, offsetY = 0, 0
    if offset is not None:
        if "x" in offset:
            offsetX = offset["x"]
        if "y" in offset:
            offsetY = offset["y"]

    if point is None:
        return

    x, y = point
    __mouse.send_data_absolute(x + offsetX, y + offsetY)
    __mouse.click()
    time.sleep(0.5)


def mouseMove(x: int, y: int):
    __mouse.send_data_absolute(x, y)
    time.sleep(1)


def clickImg(imgPath: str, offset: Offset | None = None):
    locations = Screen.match(imgPath)
    click(locations, offset)


if __name__ == "__main__":
    setup(False)
    press("Up")
    close()
#
