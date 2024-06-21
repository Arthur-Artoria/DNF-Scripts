import time
import serial
import ch9329Comm


__keyboard: ch9329Comm.keyboard.DataComm

def setup():
    global __keyboard
    
    serial.ser = serial.Serial('COM3', 115200)  # type: ignore # 开启串口
    __keyboard = ch9329Comm.keyboard.DataComm()
    __keyboard.normal_button_hex_dict["EC"] = b"\x29"
    


def close():
    serial.ser.close()  # type: ignore


def press(key: str):
    __keyboard.send_data(key)
    time.sleep(0.5)
    __keyboard.release()
    
    
if __name__ == '__main__':
    time.sleep(3)
    setup()
    press('EC')
    close()


