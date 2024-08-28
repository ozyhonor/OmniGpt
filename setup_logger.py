import logging


def setup_logger():
    logger = logging.getLogger('OmniBot_logger')
    logger.setLevel(logging.INFO)

    success_handler = logging.FileHandler('success.log')
    success_handler.setLevel(logging.INFO)

    error_handler = logging.FileHandler('error.log')
    error_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    success_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger.addHandler(success_handler)
    logger.addHandler(error_handler)

    return logger


logger = setup_logger()