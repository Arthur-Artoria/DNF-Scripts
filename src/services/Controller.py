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


def setup():
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


def press(key: str, seconds: float = 0.5):
    data = "".join(map(lambda x: Keyboard.options[x]["key"], key.split(" ")))
    __keyboard.send_data(data)
    time.sleep(seconds)
    __keyboard.release()
    time.sleep(0.5)


def release():
    __keyboard.release()


def click(locations: tuple[NDArray[np.intp], ...], offset: Offset | None = None):
    offsetX, offsetY = 0, 0
    if offset is not None:
        if "x" in offset:
            offsetX = offset["x"]
        if "y" in offset:
            offsetY = offset["y"]

    for pt in zip(*locations[::-1]):
        x, y = int(pt[0]), int(pt[1])
        __mouse.send_data_absolute(x + offsetX, y + offsetY)
        __mouse.click()
        time.sleep(0.5)
        break


def clickImg(imgPath: str, offset: Offset | None = None):
    locations = Screen.match(imgPath)
    click(locations, offset)


if __name__ == "__main__":
    time.sleep(0.5)
    setup()
    press("Up")
    close()
#
