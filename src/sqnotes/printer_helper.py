
from sqnotes.text_utility import get_wrapped_text


def print_to_so(text):
    wrapped_text = get_wrapped_text(input_text = text)
    print(wrapped_text)
    
class PrinterHelper:
    
    @staticmethod
    def print_to_so(text):
        wrapped_text = get_wrapped_text(input_text = text)
        print(wrapped_text)