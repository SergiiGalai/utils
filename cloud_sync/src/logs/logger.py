import logging


def setup_logger(level):
    logging.basicConfig(
        level=level,
        format='%(asctime)s  %(levelname)-6s %(filename)s:%(lineno)d %(funcName)s() %(message)s',
        datefmt='%y%m%d %H:%M:%S'
    )

    logger_name = str(__file__) + " :: " + str(__name__)
    logger = logging.getLogger(logger_name)
    logging.getLogger("requests").setLevel(logging.WARNING)
    return logger
