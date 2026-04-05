import enum
import logging


class ToolMode(enum.IntEnum):
    RELEASE = 0
    DEVELOPMENT = 1


def configureLogging(toolMode: ToolMode) -> logging.Logger:
    logger: logging.Logger = logging.getLogger("window_container")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    handler: logging.StreamHandler = logging.StreamHandler()

    if toolMode == ToolMode.RELEASE:
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )

    else:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
            )
        )

    logger.addHandler(handler)

    return logger

