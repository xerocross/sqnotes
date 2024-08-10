from sqnotes.sqnotes_config_module import SQNotesConfig

from injector import inject
import subprocess

class TextEditorHelper:
    @inject
    def __init__(
                    self,
                    sqnotes_config: SQNotesConfig
                 ):
        self.sqnotes_config = sqnotes_config
        
    def set_text_editor(self, text_editor):
        self._text_editor = text_editor
        
    def get_text_editor(self):
        return self._text_editor
        
    def get_input_from_text_editor(self):
        command = ['vim', 'temp_filename']
        subprocess.call(command)