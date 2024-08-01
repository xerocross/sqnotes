

from sqnotes import interface_copy
import logging
from sqnotes.user_input_helper import UserInputHelper
from injector import inject
logger = logging.getLogger("path_input_helper")

def _is_a_valid_path(input_string):
    if input_string is None or input_string == '':
        return False
    return True

PATH_VALIDATION_FAILURE = 'Input was not a valid path; please try again.'
ATTEMPT_LIMIT = 3

class PathInputHelper:
    @inject
    def __init__(self, user_input_helper : UserInputHelper):
        self.user_input_helper = user_input_helper

    
    def get_path_interactive(self):
        validation_failure_message = ""
        
        prompt = interface_copy.PROMPT_FOR_PATH()
        input_string = self.user_input_helper.get_string_input(prompt = prompt, 
                                                               validator = _is_a_valid_path, 
                                                               validation_failure_message = PATH_VALIDATION_FAILURE, 
                                                               attempt_limit = ATTEMPT_LIMIT) 
        
        
        
        
        