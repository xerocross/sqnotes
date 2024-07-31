
from sqnotes import interface_copy
from injector import inject
import pyinputplus
from sqnotes.printer_helper import PrinterHelper


class MaxInputAttemptsException(Exception):
    """Raise when the user reaches the maximum number of invalid input attempts."""



class ChooseTextEditor:
    MAX_ATTEMPTS = 3
    
    @inject
    def __init__(self, 
                 printer_helper : PrinterHelper,
                 available_editors = [], 
                 supported_editors = []
                 ):
        self.available_editors = available_editors
        self.supported_editors = supported_editors
        self.printer_helper = printer_helper

    
    def get_available_editors(self):
        return self.available_editors
    
    def set_available_editors(self, available_editors):
        self.available_editors = available_editors
        
    def set_supported_editors(self, supported_editors):
        self.supported_editors = supported_editors
    
    def choose_text_editor_interactive(self):
        available_editors = self.get_available_editors()
        
        if len(available_editors) == 0:
            message = interface_copy.NO_SUPPORTED_TEXT_EDITORS_AVAILABLE()
            message += interface_copy.SUPPORTED_TEXT_EDITORS().format(", ".join(self.supported_editors))
            message += interface_copy.PLEASE_INSTALL_TEXT_EDITOR_MESSAGE()
            self.printer_helper.print_to_so(message)
            
        elif len(available_editors) > 1:
            print(interface_copy.PLEASE_CHOOSE_EDITOR())
                
            prompt_message = interface_copy.SELECT_ONE_OF_FOLLOWING()
            try:
                selected_editor = pyinputplus.inputMenu(self.available_editors, 
                                                    prompt = prompt_message, 
                                                    limit = self.MAX_ATTEMPTS,
                                                    default = None)
            except pyinputplus.RetryLimitException:
                raise MaxInputAttemptsException()
            
            return selected_editor

        elif len(available_editors) == 1:
            only_available_editor = available_editors[0]
            message = interface_copy.ONLY_ONE_AVAILABLE_TEXT_EDITOR().format(only_available_editor)
            self.printer_helper.print_to_so(message)
            return only_available_editor
            
            
            
            