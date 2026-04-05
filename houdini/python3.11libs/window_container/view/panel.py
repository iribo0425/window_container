import logging
import pathlib

import window_container.core.window as _window
import window_container.core.win32.user32 as _user32
import window_container.model.panel_model as _panel_model
from PySide6 import QtCore, QtGui, QtQml, QtQuick, QtWidgets


_logger: logging.Logger = logging.getLogger(__name__)


class Panel(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super(Panel, self).__init__(parent)

        self.setObjectName("windowContainer")
        self.setWindowTitle("Window Container")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.__model: _panel_model.PanelModel = _panel_model.PanelModel(self)

        self.__quickView: QtQuick.QQuickView | None = None
        self.__windowContainer: QtWidgets.QWidget | None = None
        self.__overlayTarget: QtQuick.QQuickItem | None = None

        self.__overlayWindow: _window.Window | None = None
        self.__originalRect: tuple[int, int, int, int] = (0, 0, 0, 0)
        self.__originalIsTopmost: bool = False

        self.__timer: QtCore.QTimer = QtCore.QTimer(self)
        self.__timer.setInterval(100)
        self.__timer.timeout.connect(self.__timer_timeout)

        self.__model.attachWindowRequested.connect(self.__attachWindow)
        self.__model.detachWindowRequested.connect(self.__detachWindow)

        try:
            self.__quickView = QtQuick.QQuickView()
            self.__quickView.setResizeMode(QtQuick.QQuickView.ResizeMode.SizeRootObjectToView)
            self.__quickView.statusChanged.connect(self.__quickView_statusChanged)
            self.__quickView.sceneGraphError.connect(self.__quickView_sceneGraphError)

            self.__quickView.engine().setOutputWarningsToStandardError(False)
            self.__quickView.engine().warnings.connect(self.__engine_warnings)

            self.__quickView.setInitialProperties({
                "panelModel": self.__model,
            })

            qmlFilePath: pathlib.Path = pathlib.Path(__file__).resolve().parent / "qml" / "Panel.qml"
            qmlFileUrl: QtCore.QUrl = QtCore.QUrl.fromLocalFile(qmlFilePath)
            self.__quickView.setSource(qmlFileUrl)

            self.__dumpErrors()

            if self.__quickView.status() == QtQuick.QQuickView.Status.Error:
                raise RuntimeError("Failed to load QML. See log for details.")

            self.__windowContainer = QtWidgets.QWidget.createWindowContainer(self.__quickView, self)
            self.__windowContainer.setObjectName("quickWindowContainer")
            self.__windowContainer.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.__windowContainer.installEventFilter(self)

            layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.__windowContainer)

            self.__overlayTarget = self.__quickView.rootObject().findChild(QtCore.QObject, "overlayTarget")

            signalNames: tuple[str, ...] = (
                "xChanged",
                "yChanged",
                "widthChanged",
                "heightChanged",
                "visibleChanged"
            )

            for signalName in signalNames:
                signal = getattr(self.__overlayTarget, signalName, None)

                if signal is not None:
                    signal.connect(self.__overlayTargetGeometryChanged)

            self.resize(1000, 700)

        except Exception:
            self.__cleanupQuickObjects()
            raise

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.__detachWindow()
        self.__cleanupQuickObjects()
        super().closeEvent(event)

    def moveEvent(self, event: QtGui.QMoveEvent) -> None:
        super().moveEvent(event)
        self.__syncOverlayWindowGeometry(raiseWindow=True)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.__syncOverlayWindowGeometry(raiseWindow=True)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super().showEvent(event)
        self.__syncOverlayWindowGeometry(raiseWindow=True)

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        super().hideEvent(event)
        self.__syncOverlayWindowGeometry(raiseWindow=False)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched is self.__windowContainer:
            if event.type() in {
                QtCore.QEvent.Type.Move,
                QtCore.QEvent.Type.Resize,
                QtCore.QEvent.Type.Show,
                QtCore.QEvent.Type.Hide,
            }:
                self.__syncOverlayWindowGeometry(raiseWindow=True)
            return False

        return super(Panel, self).eventFilter(watched, event)

    def __cleanupQuickObjects(self) -> None:
        self.__timer.stop()
        self.__overlayTarget = None

        if self.__windowContainer is not None:
            self.__windowContainer.close()
            self.__windowContainer.deleteLater()
            self.__windowContainer = None

        if self.__quickView is not None:
            self.__quickView.close()
            self.__quickView.deleteLater()
            self.__quickView = None

    def __resetOverlayState(self) -> None:
        self.__overlayWindow = None
        self.__originalRect = (0, 0, 0, 0)
        self.__originalIsTopmost = False
        self.__model.setIsWindowAttached(False)

    @QtCore.Slot()
    def __overlayTargetGeometryChanged(self) -> None:
        self.__syncOverlayWindowGeometry(raiseWindow=True)

    @QtCore.Slot(int)
    def __attachWindow(self, hwnd: int) -> None:
        overlayWindow: _window.Window = _window.Window(hwnd)

        if not overlayWindow.isValid():
            QtWidgets.QMessageBox.warning(
                self,
                "Window Container",
                "The selected window no longer exists.",
            )
            return

        if (
            (self.__overlayWindow is not None)
            and (self.__overlayWindow.getHandle() == hwnd)
        ):
            self.__syncOverlayWindowGeometry(raiseWindow=True)
            return

        try:
            state: _window.WindowState = overlayWindow.getState()

            if state in (_window.WindowState.MINIMIZED, _window.WindowState.MAXIMIZED):
                overlayWindow.show(_user32.SW_RESTORE)

                if not overlayWindow.isValid():
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Window Container",
                        "Failed to restore the selected window.",
                    )
                    return

                restoredState: _window.WindowState = overlayWindow.getState()

                if restoredState in (_window.WindowState.MINIMIZED, _window.WindowState.MAXIMIZED):
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Window Container",
                        "Failed to restore the selected window.",
                    )
                    return

            self.__detachWindow()

            self.__overlayWindow = overlayWindow
            self.__originalRect = self.__overlayWindow.getRect()
            self.__originalIsTopmost = self.__overlayWindow.getIsTopmost()

            self.__overlayWindow.show(_user32.SW_SHOW)
            self.__overlayWindow.setIsTopmost(True)

            self.__syncOverlayWindowGeometry(raiseWindow=True)

            if self.__overlayWindow is None:
                return

            self.__timer.start()
            self.__model.setIsWindowAttached(True)

            _logger.info(
                "Attached overlay window. hwnd=%s",
                self.__overlayWindow.getHandle(),
            )

        except Exception as exception:
            _logger.exception("Failed to attach overlay window. hwnd=%s", hwnd)
            self.__resetOverlayState()

            QtWidgets.QMessageBox.critical(
                self,
                "Window Container",
                f"Failed to attach the selected window.\n\n{exception}",
            )

    @QtCore.Slot()
    def __detachWindow(self) -> None:
        self.__timer.stop()

        try:
            if ((self.__overlayWindow is not None)
                and self.__overlayWindow.isValid()
            ):
                left, top, right, bottom = self.__originalRect

                self.__overlayWindow.setIsTopmost(self.__originalIsTopmost)
                self.__overlayWindow.setPos(
                    _user32.HWND_TOPMOST if self.__originalIsTopmost else _user32.HWND_NOTOPMOST,
                    left,
                    top,
                    max(1, right - left),
                    max(1, bottom - top),
                    _user32.SWP_NOACTIVATE | _user32.SWP_SHOWWINDOW,
                )
                self.__overlayWindow.show(_user32.SW_SHOW)

                _logger.info("Detached overlay window. hwnd=%s", self.__overlayWindow.getHandle())

        except Exception:
            _logger.exception(
                "Failed to detach overlay window cleanly. hwnd=%s",
                self.__overlayWindow.getHandle() if self.__overlayWindow is not None else None,
            )

        finally:
            self.__resetOverlayState()

    def __syncOverlayWindowGeometry(self, raiseWindow: bool) -> None:
        if self.__overlayWindow is None:
            return

        if not self.__overlayWindow.isValid():
            self.__timer.stop()
            self.__resetOverlayState()
            return

        state: _window.WindowState = self.__overlayWindow.getState()

        if state in (_window.WindowState.MINIMIZED, _window.WindowState.MAXIMIZED):
            self.__timer.stop()
            self.__overlayWindow.setIsTopmost(self.__originalIsTopmost)
            self.__resetOverlayState()
            return

        if ((self.__overlayTarget is None)
            or (self.__windowContainer is None)
        ):
            return

        if (
            not self.isVisible()
            or not self.__windowContainer.isVisible()
            or not bool(self.__overlayTarget.property("visible"))
        ):
            self.__overlayWindow.show(_user32.SW_HIDE)
            return

        width: int = max(0, int(round(float(self.__overlayTarget.property("width")))))
        height: int = max(0, int(round(float(self.__overlayTarget.property("height")))))

        if ((width <= 0)
            or (height <= 0)
        ):
            self.__overlayWindow.show(_user32.SW_HIDE)
            return

        scenePosition: QtCore.QPointF = self.__overlayTarget.mapToScene(QtCore.QPointF(0.0, 0.0))
        containerPoint: QtCore.QPoint = QtCore.QPoint(
            int(round(scenePosition.x())),
            int(round(scenePosition.y())),
        )
        globalPoint: QtCore.QPoint = self.__windowContainer.mapToGlobal(containerPoint)
        rect: QtCore.QRect = QtCore.QRect(globalPoint.x(), globalPoint.y(), width, height)

        flags: int = _user32.SWP_NOACTIVATE | _user32.SWP_SHOWWINDOW
        insertAfter: int = _user32.HWND_TOPMOST

        if not raiseWindow:
            flags |= _user32.SWP_NOZORDER

        _logger.debug(
            "Sync overlay geometry: hwnd=%s x=%s y=%s w=%s h=%s raise=%s",
            self.__overlayWindow.getHandle(),
            rect.x(),
            rect.y(),
            rect.width(),
            rect.height(),
            raiseWindow,
        )

        try:
            self.__overlayWindow.setPos(
                insertAfter,
                rect.x(),
                rect.y(),
                max(1, rect.width()),
                max(1, rect.height()),
                flags,
            )
            self.__overlayWindow.show(_user32.SW_SHOW)

        except Exception:
            _logger.exception("Failed to sync overlay geometry. hwnd=%s", self.__overlayWindow.getHandle())

    @QtCore.Slot()
    def __timer_timeout(self) -> None:
        self.__syncOverlayWindowGeometry(raiseWindow=True)

    def __quickView_statusChanged(self, status: QtQuick.QQuickView.Status) -> None:
        _logger.debug("QQuickView status changed: %s", status)
        self.__dumpErrors()

    def __quickView_sceneGraphError(self, error: QtQuick.QQuickWindow.SceneGraphError, message: str) -> None:
        errorNameMap: dict[QtQuick.QQuickWindow.SceneGraphError, str] = {
            QtQuick.QQuickWindow.SceneGraphError.ContextNotAvailable: "ContextNotAvailable",
        }
        errorName: str = errorNameMap.get(error, str(error))
        fullMessage: str = (
            "A Qt Quick scene graph error occurred.\n\n"
            f"Error: {errorName}\n"
            f"Message: {message}"
        )

        _logger.critical(
            "QQuickView scene graph error. error=%s message=%s",
            errorName,
            message,
        )

        QtWidgets.QMessageBox.critical(
            self,
            "Window Container",
            fullMessage,
        )

        self.setEnabled(False)
        self.close()

    def __engine_warnings(self, warnings: list[QtQml.QQmlError]) -> None:
        if not warnings:
            return

        _logger.warning("QQmlEngine emitted %d warning(s)", len(warnings))

        for warning in warnings:
            _logger.warning("QML warning: %s", warning.toString())

    def __dumpErrors(self) -> None:
        if self.__quickView is None:
            return

        if self.__quickView.status() != QtQuick.QQuickView.Status.Error:
            return

        errors: list[QtQml.QQmlError] = self.__quickView.errors()

        if not errors:
            _logger.error("QQuickView status is Error, but errors() is empty")
            return

        for error in errors:
            _logger.error("QML error: %s", error.toString())


