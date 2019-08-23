import logging
import os

LOG_DIR = "../logs"

def get_logger(name, log_name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s %(name)s: %(asctime)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.WARNING)
    logger.addHandler(sh)

    abs_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_DIR)
    if not os.path.exists(abs_log_dir):
        os.makedirs(abs_log_dir)

    fh = logging.FileHandler(os.path.join(abs_log_dir, log_name))
    fh.setFormatter(formatter)
    # fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger
