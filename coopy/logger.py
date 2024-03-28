import sys, logging
from logging.handlers import RotatingFileHandler


def default_logger(logger):
    logger.setLevel(logging.INFO)

    # File handler configuration
    file_handler = RotatingFileHandler('logger.txt', maxBytes=1024*1024*5, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))

    # Stream (console) handler configuration
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))

    # Adding handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)