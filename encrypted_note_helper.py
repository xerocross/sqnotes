
import tempfile
import subprocess
import logging
import sys
import os
from injector import inject

DEBUGGING = False

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    if DEBUGGING:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)  # Log all levels to console
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

class GPGSubprocessException(Exception):
    """Raise when an exception or error occurs in calling gpg in a subprocess."""
    
class EncryptedNoteHelper:
    
    @inject
    def __init__(self):
        pass
    
    def write_encrypted_note(self, note_file_path, note_content, config):
        with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
            temp_enc_filename = temp_enc_file.name
            temp_enc_file.write(note_content.encode('utf-8'))
            
        
        GPG_KEY_EMAIL = config['GPG_KEY_EMAIL']
            
        subprocess_command = ['gpg', '--yes','--quiet', '--batch', '--output', note_file_path, '--encrypt', '--recipient', GPG_KEY_EMAIL, temp_enc_filename]
        if 'USE_ASCII_ARMOR' in config and config['USE_ASCII_ARMOR']:
            subprocess_command.insert(1, '--armor')
            
        try:
            response = subprocess.call(subprocess_command)
            self._delete_temp_file(temp_file=temp_enc_filename)
            if response != 0:
                raise GPGSubprocessException()
        except Exception as e:
            logger.error(e)
            self._delete_temp_file(temp_file=temp_enc_filename)
            raise GPGSubprocessException()
        
        
    def _delete_temp_file(self, temp_file):
        if os.path.exists(temp_file):
                os.remove(temp_file)
                
        