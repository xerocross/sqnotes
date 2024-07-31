
from pyinputplus import inputStr
from sqnotes import interface_copy
import logging

logger = logging.getLogger("path_input_helper")

def _is_a_valid_path(input_string):
    return input_string


class PathInputHelper:
    
    

    
    def get_path_interactive(self):
        
        
        prompt = interface_copy.PROMPT_FOR_PATH()
        input_string = inputStr(prompt = prompt, applyFunc = _is_a_valid_path)
        
        