from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Final, TypeAlias


_dll: ctypes.WinDLL = ctypes.WinDLL("user32", use_last_error=True)


Hwnd: TypeAlias = int


EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


EnumWindows = _dll.EnumWindows
EnumWindows.argtypes = [
    EnumWindowsProc,
    wintypes.LPARAM
]
EnumWindows.restype = wintypes.BOOL

IsWindow = _dll.IsWindow
IsWindow.argtypes = [
    wintypes.HWND
]
IsWindow.restype = wintypes.BOOL

IsWindowVisible = _dll.IsWindowVisible
IsWindowVisible.argtypes = [
    wintypes.HWND
]
IsWindowVisible.restype = wintypes.BOOL

IsIconic = _dll.IsIconic
IsIconic.argtypes = [
    wintypes.HWND
]
IsIconic.restype = wintypes.BOOL

IsZoomed = _dll.IsZoomed
IsZoomed.argtypes = [
    wintypes.HWND
]
IsZoomed.restype = wintypes.BOOL

GetWindowTextLengthW = _dll.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = [
    wintypes.HWND
]
GetWindowTextLengthW.restype = ctypes.c_int

GetWindowTextW = _dll.GetWindowTextW
GetWindowTextW.argtypes = [
    wintypes.HWND,
    wintypes.LPWSTR,
    ctypes.c_int
]
GetWindowTextW.restype = ctypes.c_int

GetClassNameW = _dll.GetClassNameW
GetClassNameW.argtypes = [
    wintypes.HWND,
    wintypes.LPWSTR,
    ctypes.c_int
]
GetClassNameW.restype = ctypes.c_int

GetWindowThreadProcessId = _dll.GetWindowThreadProcessId
GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.DWORD)
]
GetWindowThreadProcessId.restype = wintypes.DWORD

GetAncestor = _dll.GetAncestor
GetAncestor.argtypes = [
    wintypes.HWND,
    ctypes.c_uint
]
GetAncestor.restype = wintypes.HWND

GetWindowRect = _dll.GetWindowRect
GetWindowRect.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.RECT)
]
GetWindowRect.restype = wintypes.BOOL

SetWindowPos = _dll.SetWindowPos
SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint,
]
SetWindowPos.restype = wintypes.BOOL

ShowWindow = _dll.ShowWindow
ShowWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_int
]
ShowWindow.restype = wintypes.BOOL

EnumChildWindows = _dll.EnumChildWindows
EnumChildWindows.argtypes = [
    wintypes.HWND,
    EnumWindowsProc,
    wintypes.LPARAM,
]
EnumChildWindows.restype = wintypes.BOOL

GetWindowLongPtr = _dll.GetWindowLongPtrW
GetWindowLongPtr.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
]
GetWindowLongPtr.restype = ctypes.c_ssize_t


GA_ROOT: Final[int] = 2

GWL_EXSTYLE: Final[int] = -20

HWND_TOP: Final[int] = 0
HWND_TOPMOST: Final[int] = -1
HWND_NOTOPMOST: Final[int] = -2

WS_EX_TOPMOST: Final[int] = 0x00000008

SW_HIDE: Final[int] = 0
SW_SHOWNORMAL: Final[int] = 1
SW_SHOWMINIMIZED: Final[int] = 2
SW_SHOWMAXIMIZED: Final[int] = 3
SW_SHOWNOACTIVATE: Final[int] = 4
SW_SHOW: Final[int] = 5
SW_MINIMIZE: Final[int] = 6
SW_SHOWMINNOACTIVE: Final[int] = 7
SW_SHOWNA: Final[int] = 8
SW_RESTORE: Final[int] = 9
SW_SHOWDEFAULT: Final[int] = 10
SW_FORCEMINIMIZE: Final[int] = 11

SWP_NOSIZE: Final[int] = 0x0001
SWP_NOMOVE: Final[int] = 0x0002
SWP_NOZORDER: Final[int] = 0x0004
SWP_NOACTIVATE: Final[int] = 0x0010
SWP_SHOWWINDOW: Final[int] = 0x0040