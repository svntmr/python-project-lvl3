import logging


def get_logger(module_name: str, level=logging.ERROR) -> logging.Logger:
    logger = logging.getLogger(module_name)
    logger.handlers.clear()
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
