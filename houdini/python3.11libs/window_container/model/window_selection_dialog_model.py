import copy
import enum
import window_container.core.window as _window
from PySide6 import QtCore


class WindowListModelRole(enum.IntEnum):
    HANDLE = QtCore.Qt.UserRole + 1
    PID = QtCore.Qt.UserRole + 2
    TEXT = QtCore.Qt.UserRole + 3


class WindowListModel(QtCore.QAbstractListModel):
    currentIndexChanged: QtCore.Signal = QtCore.Signal(int)


    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super(WindowListModel, self).__init__(parent)

        self.__rows: list[_window.Window] = []
        self.__currentIndex: int = -1


    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self.__rows)


    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> object:
        if not self.__isValidIndex(index):
            return None

        row: _window.Window = self.__rows[index.row()]

        if role == WindowListModelRole.HANDLE:
            return row.getHandle()

        if role == WindowListModelRole.PID:
            return row.getPid()

        if role == WindowListModelRole.TEXT:
            return row.getText()

        return None


    def roleNames(self) -> dict[int, bytes]:
        return {
            WindowListModelRole.HANDLE: b"handle",
            WindowListModelRole.PID: b"pid",
            WindowListModelRole.TEXT: b"text",
        }


    def getCurrentIndex(self) -> int:
        return self.__currentIndex


    def setCurrentIndex(self, index: int) -> None:
        if not self.__isValidRowIndex(index):
            index = -1

        if index == self.__currentIndex:
            return

        self.__currentIndex = index
        self.currentIndexChanged.emit(index)


    currentIndex: QtCore.Property = QtCore.Property(
        int,
        getCurrentIndex,
        setCurrentIndex,
        notify=currentIndexChanged
    )


    def setRows(self, rows: list[_window.Window]) -> None:
        self.beginResetModel()
        self.__rows = copy.deepcopy(rows)
        self.__currentIndex = -1
        self.endResetModel()
        self.currentIndexChanged.emit(-1)


    def currentWindow(self) -> _window.Window | None:
        if not self.__isValidRowIndex(self.__currentIndex):
            return None

        return self.__rows[self.__currentIndex]


    def __isValidRowIndex(self, rowIndex: int) -> bool:
        return 0 <= rowIndex < len(self.__rows)


    def __isValidIndex(self, index: QtCore.QModelIndex) -> bool:
        return (
            index.isValid()
            and (index.column() == 0)
            and self.__isValidRowIndex(index.row())
        )


class WindowSelectionDialogModel(QtCore.QObject):
    accepted: QtCore.Signal = QtCore.Signal()
    rejected: QtCore.Signal = QtCore.Signal()


    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super(WindowSelectionDialogModel, self).__init__(parent)

        self.__listModel: WindowListModel = WindowListModel(self)


    def getListModel(self) -> WindowListModel:
        return self.__listModel


    listModel: QtCore.Property = QtCore.Property(
        QtCore.QObject,
        getListModel,
        constant=True,
    )


    @QtCore.Slot()
    def accept(self) -> None:
        self.accepted.emit()


    @QtCore.Slot()
    def reject(self) -> None:
        self.rejected.emit()


    def setWindows(self, windows: list[_window.Window]) -> None:
        self.__listModel.setRows(windows)


    def currentWindow(self) -> _window.Window | None:
        return self.__listModel.currentWindow()

