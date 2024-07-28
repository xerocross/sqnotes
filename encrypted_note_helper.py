
import tempfile
import subprocess
import logging
import sys
import os
from injector import inject

from sqnotes_logger import SQNotesLogger

class GPGSubprocessException(Exception):
    """Raise when an exception or error occurs in calling gpg in a subprocess."""
    
class CouldNotReadNoteException(Exception):
    """Raise when encounter an error attempting to read note file."""
    
class EncryptedNoteHelper:
    
    @inject
    def __init__(self, sqnotes_logger : SQNotesLogger):
        self.logger = sqnotes_logger.get_logger(__name__)
    
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
            self.logger.error(e)
            self._delete_temp_file(temp_file=temp_enc_filename)
            raise GPGSubprocessException()
        
        
    def get_decrypted_content_in_memory(self, note_path):
        self.logger.debug("attempting to use in-memory decryption")
        
        try:
            with open(note_path, 'rb') as f:
                encrypted_data = f.read()
        except Exception as e:
            self.logger.error("encountered an error attempting to read encrypted note")
            self.logger.error(e)
            raise CouldNotReadNoteException()
        try:
            gpg_command = ['gpg','--batch', '--decrypt']
            process = subprocess.run(
                gpg_command,
                input=encrypted_data,
                text=False,  # binary mode
                capture_output=True,
                check=True
            )
            if process.returncode != 0:
                self.logger.error(f"GPG exited with code {process.returncode}")
                raise GPGSubprocessException()
            
            decrypted_data = process.stdout
            decrypted_text = decrypted_data.decode('utf-8')
            return decrypted_text
        except subprocess.CalledProcessError as e:
            self.logger.error(f"GPG failed with return code {e.returncode}")
            error_message = "Error message: " + e.stderr.decode()
            self.logger.error(error_message)
            raise GPGSubprocessException()
        except Exception as e:
            self.logger.error("encountered an error while decrypting")
            self.logger.error(e)
            raise GPGSubprocessException()
        
        
    def _delete_temp_file(self, temp_file):
        if os.path.exists(temp_file):
                os.remove(temp_file)
                
        