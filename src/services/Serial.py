from multiprocessing import Queue
import time
from typing import Any, Literal, Optional
import serial
import ch9329Comm
from services import Screen
from constants import Keyboard, Monitor

type Offset = tuple[int, int]

type Instruction = tuple[
    Literal[1, 2, 3, 4],
    Any,
    Optional[Offset],
]

INSTRUCTION_PRESS = 1
INSTRUCTION_RELEASE = 2
INSTRUCTION_CLICK = 3
INSTRUCTION_MOUSE_MOVE = 4

__mouse: ch9329Comm.mouse.DataComm
__keyboard: ch9329Comm.keyboard.DataComm
__stopFlag: bool = False
__prevPressKey: str | None = None


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


def worker(queue: Queue):
    try:
        setup()
        while True:
            instruction = queue.get()
            if instruction is None or __stopFlag is True:
                __stop()
                break
            else:
                __handleInstruction(instruction)
    except:
        __stop()


def __handleInstruction(instruction: Instruction):
    if instruction[0] == INSTRUCTION_PRESS:
        press(instruction[1])
    elif instruction[0] == INSTRUCTION_RELEASE:
        print("释放按键")
        release()
    elif instruction[0] == INSTRUCTION_CLICK:
        click(instruction[1], instruction[2])
    elif instruction[0] == INSTRUCTION_MOUSE_MOVE:
        mouseMove(instruction[1])


def __stop():
    release()
    serial.ser.close()  # type: ignore


def close():
    global __stopFlag
    __stopFlag = True


def press(key: str):
    global __keyboard
    global __prevPressKey

    if key == __prevPressKey:
        return
    else:
        __keyboard.release()
        __prevPressKey = key
        __keyboard.send_data(key)


def release():
    global __keyboard
    global __prevPressKey
    __prevPressKey = None
    __keyboard.release()


def click(
    point: Screen.Point | None,
    offset: Offset | None = None,
):
    if point is None:
        return

    x, y = point
    offsetX, offsetY = 0, 0

    if offset:
        offsetX, offsetY = offset

    __mouse.send_data_absolute(x + offsetX, y + offsetY)
    __mouse.click()


def mouseMove(point: tuple[int, int]):
    x, y = point
    __mouse.send_data_absolute(x, y)
