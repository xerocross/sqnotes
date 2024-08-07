
import tempfile
import subprocess
import os
from injector import inject

from sqnotes.sqnotes_logger import SQNotesLogger

class GPGSubprocessException(Exception):
    """Raise when an exception or error occurs in calling gpg in a subprocess."""
    
class CouldNotReadNoteException(Exception):
    """Raise when encounter an error attempting to read note file."""
    
class EncryptedNoteHelper:
    
    @inject
    def __init__(self, sqnotes_logger : SQNotesLogger):
        self.logger = sqnotes_logger.get_logger(__name__)
        
    
    def _call_gpg_subprocess_to_write_encrypted(self, in_commands):
        note_file_path = in_commands['output_path']
        GPG_KEY_EMAIL = in_commands['GPG_KEY_EMAIL']
        infile = in_commands['infile']
        subprocess_command = ['gpg', 
                              '--yes',
                              '--quiet', 
                              '--batch', 
                              '--output', 
                              note_file_path, 
                              '--encrypt', 
                              '--recipient', 
                              GPG_KEY_EMAIL, 
                              infile]
        
        if 'USE_ASCII_ARMOR' in in_commands and in_commands['USE_ASCII_ARMOR'] == 'yes':
            subprocess_command.insert(1, '--armor')
        
        return subprocess.call(subprocess_command)
        
        
    def _get_temp_plaintext_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_plaintext_file:
            temp_file_path = temp_plaintext_file.name
        return temp_file_path
        
        
    def _write_plaintext_to_temp_file(self, note_content, config=None):
        self.logger.debug(f"about to write  '{note_content}' to temp file")
            
        temp_enc_filename = self._get_temp_plaintext_file()
        self.logger.debug(f"tempfile name: {temp_enc_filename}")
        with open(temp_enc_filename, 'w') as open_tempfile:
            open_tempfile.write(note_content)
        return temp_enc_filename
    
    def write_encrypted_note(self, note_file_path, note_content, config):
        temp_enc_filename = self._write_plaintext_to_temp_file(
                                            note_content = note_content, 
                                            config = config)
        self.logger.debug(f"printed to temp file: {temp_enc_filename}")
        gpg_in_commands = {
            'GPG_KEY_EMAIL' : config['GPG_KEY_EMAIL'],
            'output_path' : note_file_path,
            'infile' : str(temp_enc_filename)
        }
        if 'USE_ASCII_ARMOR' in config:
            gpg_in_commands['USE_ASCII_ARMOR'] = config['USE_ASCII_ARMOR']
            
        try:
            response = self._call_gpg_subprocess_to_write_encrypted(in_commands = gpg_in_commands)
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
        
        
    def decrypt_note_into_temp_file(self, note_path):
        with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
            temp_dec_filename = temp_dec_file.name
        try:
            decrypt_process = subprocess.call(['gpg', '--yes','--quiet', '--batch', '--output', temp_dec_filename, '--decrypt', note_path])
        except Exception as e:
            self.logger.error(e)
            self._delete_temp_file(temp_file=temp_dec_filename)
            raise GPGSubprocessException()
        
        if decrypt_process != 0:
            self.logger.error(f"decrypt process returned code {decrypt_process}")
            self._delete_temp_file(temp_file=temp_dec_filename)
            raise GPGSubprocessException()
        
        return temp_dec_filename
        
    def _delete_temp_file(self, temp_file):
        if os.path.exists(temp_file):
                os.remove(temp_file)
                
        