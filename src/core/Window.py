import win32gui

__handler: int
__rect: tuple[int, int, int, int]


def setWindow():
    __getWindow()
    __openController()
    __setWindowSize()
    __moveWindow()


def __getWindow():
    global __handler
    # TODO：应该改成 DNF 的窗口标题
    __handler = win32gui.FindWindow(None, "文件资源管理器")
    win32gui.SetForegroundWindow(__handler)


# TODO：发送 ESC 按键，打开控制菜单
def __openController():
    pass


def __setWindowSize():
    global __rect
    # TODO：通过游戏菜单调整游戏窗口大小
    __rect = win32gui.GetWindowRect(__handler)


def __moveWindow():
    left, top, right, bottom = __rect
    width = right - left
    height = bottom - top
    win32gui.MoveWindow(__handler, -8, -1, width, height, True)
