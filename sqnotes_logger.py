
import logging
import sys


class SQNotesLogger:

    
    def __init__(self):
        self.loggers = []
        self.debug = False
        
    def __apply_handler_config(self, logger):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        for handler in logger.handlers[:]:
                logger.removeHandler(handler)
    
        if self.debug:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)  # Log all levels to console
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
    def configure(self, debug):
        self.debug = debug
        
        for logger in self.loggers:
            logger.setLevel(logging.DEBUG)
            self.__apply_handler_config(logger)
            

    def get_logger(self, name):
        logger = logging.getLogger(name)
        self.loggers.append(logger)
        logger.setLevel(logging.DEBUG)
        self.__apply_handler_config(logger)
        return logger
    
    
    