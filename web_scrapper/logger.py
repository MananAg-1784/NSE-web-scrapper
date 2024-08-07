import logging

def create_logger():
    '''
    Creating and initializing the logger
    Log file : Logs.log
    log Levels : info / warning / error
    '''
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='logs.log',  
        level=logging.DEBUG,
        encoding='utf-8', 
        filemode='w',
        format='[%(asctime)s] | %(levelname)s | %(funcName)s >>> %(message)s',
        datefmt="%B %d, %H:%M:%S",)

    logger.info("Logger configured...")
    return logger

logger = create_logger()