import logging
import window_container.core.system as _system
import window_container.view.panel as _panel
from PySide6 import QtWidgets
from window_container.core.system import ToolMode


logger: logging.Logger = logging.getLogger(__name__)


def createPanel(toolMode: ToolMode) -> QtWidgets.QWidget:
    try:
        _system.configureLogging(toolMode)
        panel: _panel.Panel = _panel.Panel()

        return panel

    except Exception:
        logger.exception("Failed to initialize Window Container")

        QtWidgets.QMessageBox.critical(
            None,
            "Window Container",
            "Failed to initialize Window Container.\n\nSee log for details.",
        )

        raise

