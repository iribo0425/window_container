import ctypes
import enum
from ctypes import wintypes

import window_container.core.win32.user32 as _user32
from window_container.core.win32.user32 import Hwnd


class WindowState(enum.IntEnum):
    NORMAL = 0
    MAXIMIZED = 1
    MINIMIZED = 2


class Window(object):
    def __init__(self, handle: Hwnd):
        super(Window, self).__init__()
        self.__handle: Hwnd = handle

    def isValid(self) -> bool:
        return bool(_user32.IsWindow(self.__handle))

    def getHandle(self) -> Hwnd:
        return self.__handle

    def getPid(self) -> int:
        if not self.isValid():
            return 0

        processId: wintypes.DWORD = wintypes.DWORD(0)
        _user32.GetWindowThreadProcessId(self.__handle, ctypes.byref(processId))
        return processId.value

    def getText(self) -> str:
        if not self.isValid():
            return ""

        textLength: int = _user32.GetWindowTextLengthW(self.__handle)
        buffer = ctypes.create_unicode_buffer(textLength + 1)
        _user32.GetWindowTextW(self.__handle, buffer, len(buffer))
        return buffer.value

    def getIsTopLevel(self) -> bool:
        if not self.isValid():
            return False

        return _user32.GetAncestor(self.__handle, _user32.GA_ROOT) == self.__handle

    def getIsVisible(self) -> bool:
        if not self.isValid():
            return False

        return bool(_user32.IsWindowVisible(self.__handle))

    def getState(self) -> WindowState:
        if not self.isValid():
            return WindowState.NORMAL

        if _user32.IsIconic(self.__handle):
            return WindowState.MINIMIZED

        if _user32.IsZoomed(self.__handle):
            return WindowState.MAXIMIZED

        return WindowState.NORMAL

    def getRect(self) -> tuple[int, int, int, int]:
        if not self.isValid():
            return 0, 0, 0, 0

        rect: wintypes.RECT = wintypes.RECT()

        if not _user32.GetWindowRect(self.__handle, ctypes.byref(rect)):
            return 0, 0, 0, 0

        return rect.left, rect.top, rect.right, rect.bottom

    def setPos(self, insertAfter: int, x: int, y: int, cx: int, cy: int, flags: int) -> None:
        if not self.isValid():
            return

        _user32.SetWindowPos(self.__handle, insertAfter, x, y, cx, cy, flags)

    def show(self, cmdShow: int) -> None:
        if not self.isValid():
            return

        _user32.ShowWindow(self.__handle, cmdShow)

    def getIsTopmost(self) -> bool:
        if not self.isValid():
            return False

        ctypes.set_last_error(0)
        exStyle: int = int(_user32.GetWindowLongPtr(self.__handle, _user32.GWL_EXSTYLE))
        lastError: int = ctypes.get_last_error()

        if exStyle == 0 and lastError != 0:
            return False

        return bool(exStyle & _user32.WS_EX_TOPMOST)

    def setIsTopmost(self, topmost: bool) -> None:
        if not self.isValid():
            return

        insertAfter: int = _user32.HWND_TOPMOST if topmost else _user32.HWND_NOTOPMOST
        self.setPos(
            insertAfter,
            0,
            0,
            0,
            0,
            _user32.SWP_NOMOVE | _user32.SWP_NOSIZE | _user32.SWP_NOACTIVATE,
        )


def getWindows() -> list[Window]:
    windows: list[Window] = []

    @_user32.EnumWindowsProc
    def childFunc(hwnd: wintypes.HWND, lParam: wintypes.LPARAM) -> wintypes.BOOL:
        del lParam

        handle: Hwnd = int(hwnd)

        if _user32.IsWindow(handle):
            windows.append(Window(handle))

        return True

    @_user32.EnumWindowsProc
    def enumTopLevelFunc(hwnd: wintypes.HWND, lParam: wintypes.LPARAM) -> wintypes.BOOL:
        del lParam

        handle: Hwnd = int(hwnd)

        if not _user32.IsWindow(handle):
            return True

        windows.append(Window(handle))
        _user32.EnumChildWindows(handle, childFunc, 0)
        return True

    if not _user32.EnumWindows(enumTopLevelFunc, 0):
        raise ctypes.WinError(ctypes.get_last_error())

    return windows