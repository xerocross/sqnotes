
import subprocess
import logging


logger = logging.getLogger('command_validator')
logger.setLevel(logging.DEBUG)

class CommandValidator:
    
    @staticmethod
    def verify_command(command_string):
        command = [command_string, '--version']
        try:
            subprocess.call(command,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(e)
            return False
        return True
    
    @staticmethod
    def verify_vim():
        return CommandValidator.verify_command(command_string='vim')

    @staticmethod
    def verify_nano():
        return CommandValidator.verify_command(command_string='nano')
    
    @staticmethod
    def get_validator_by_command(command_string):
        validator = {
            'vim' : CommandValidator.verify_vim,
            'nano' : CommandValidator.verify_nano
        }
        if command_string in validator:
            return validator[command_string]
        else:
            return None
        
    