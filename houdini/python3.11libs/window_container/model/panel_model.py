import window_container.core.window as _window
import window_container.model.window_selection_dialog_model as _window_selection_dialog_model
from PySide6 import QtCore


class PanelModel(QtCore.QObject):
    openWindowSelectionDialogRequested: QtCore.Signal = QtCore.Signal()
    attachWindowRequested: QtCore.Signal = QtCore.Signal(int)
    detachWindowRequested: QtCore.Signal = QtCore.Signal()
    isWindowAttachedChanged: QtCore.Signal = QtCore.Signal(bool)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super(PanelModel, self).__init__(parent)

        self.__windowSelectionDialogModel: _window_selection_dialog_model.WindowSelectionDialogModel = _window_selection_dialog_model.WindowSelectionDialogModel(self)
        self.__windowSelectionDialogModel.accepted.connect(self.__windowSelectionDialogModel_accepted)
        self.__windowSelectionDialogModel.rejected.connect(self.__windowSelectionDialogModel_rejected)

        self.__isWindowAttached: bool = False

    def getWindowSelectionDialogModel(self) -> _window_selection_dialog_model.WindowSelectionDialogModel:
        return self.__windowSelectionDialogModel

    windowSelectionDialogModel: QtCore.Property = QtCore.Property(
        QtCore.QObject,
        getWindowSelectionDialogModel,
        constant=True,
    )

    def getIsWindowAttached(self) -> bool:
        return self.__isWindowAttached

    def setIsWindowAttached(self, value: bool) -> None:
        if value == self.__isWindowAttached:
            return

        self.__isWindowAttached = value
        self.isWindowAttachedChanged.emit(value)

    isWindowAttached: QtCore.Property = QtCore.Property(
        bool,
        getIsWindowAttached,
        notify=isWindowAttachedChanged,
    )

    @QtCore.Slot()
    def openWindowSelectionDialog(self) -> None:
        currentPid: int = int(QtCore.QCoreApplication.applicationPid())
        windows: list[_window.Window] = _window.getWindows()
        unfilteredWindows: list[_window.Window] = []

        for window in windows:
            if not window.getIsTopLevel():
                continue

            if window.getPid() == currentPid:
                continue

            if not window.getIsVisible():
                continue

            if window.getState() == _window.WindowState.MINIMIZED:
                continue

            text: str = window.getText().strip()

            if not text:
                continue

            left, top, right, bottom = window.getRect()
            width: int = right - left
            height: int = bottom - top

            if width <= 0 or height <= 0:
                continue

            unfilteredWindows.append(window)

        unfilteredWindows = sorted(unfilteredWindows, key=lambda w: w.getText().casefold())
        self.__windowSelectionDialogModel.setWindows(unfilteredWindows)
        self.openWindowSelectionDialogRequested.emit()

    @QtCore.Slot()
    def detachWindow(self) -> None:
        self.detachWindowRequested.emit()

    def __windowSelectionDialogModel_accepted(self) -> None:
        window: _window.Window | None = self.__windowSelectionDialogModel.currentWindow()

        if window is None:
            return

        self.attachWindowRequested.emit(window.getHandle())

    def __windowSelectionDialogModel_rejected(self) -> None:
        pass