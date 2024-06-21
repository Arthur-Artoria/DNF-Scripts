import time
import numpy as np
from numpy._typing import NDArray
import serial
import ch9329Comm
import Screen

__keyboard: ch9329Comm.keyboard.DataComm


def setup():
    global __keyboard

    serial.ser = serial.Serial("COM3", 115200)  # type: ignore # 开启串口
    __keyboard = ch9329Comm.keyboard.DataComm()
    __keyboard.normal_button_hex_dict["EC"] = b"\x29"


def close():
    serial.ser.close()  # type: ignore


def press(key: str):
    __keyboard.send_data(key)
    time.sleep(0.5)
    __keyboard.release()


def click(locations: tuple[NDArray[np.intp], ...]):
    pass


def clickImg(imgPath: str):
    locations = Screen.match(imgPath)
    click(locations)


if __name__ == "__main__":
    time.sleep(3)
    setup()
    press("EC")
    close()
