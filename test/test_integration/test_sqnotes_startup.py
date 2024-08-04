

from sqnotes.injection_configuration_module import InjectionConfigurationModule
from sqnotes.sqnotes_module import SQNotes
from injector import Injector, provider
import pytest
import os
import yaml
from unittest.mock import patch
from sqnotes.sqnotes_config_module import SQNotesConfig
from sqnotes.user_configuration_helper import UserConfigurationHelper
from sqnotes.encrypted_note_helper import EncryptedNoteHelper


current_dir = os.path.dirname(os.path.abspath(__file__))
test_package_dir = os.path.abspath(os.path.join(current_dir, "../"))
root_dir = os.path.join(test_package_dir, "../")
sqnotes_dir = os.path.join(root_dir, "src/sqnotes")
primary_config_file_path = os.path.join(sqnotes_dir, 'config.yaml')
test_config_path = os.path.join(test_package_dir, 'resources/test_config.yaml')



def describe_sqnotes():
    
    def describe_get_init_globals_from_config():
        
        
        def it_gets_initialized_no(
                        sqnotes_real : SQNotes
                        ):
            initial_globals = sqnotes_real._get_initial_globals_from_config()
            assert initial_globals['initialized'] == 'no'
        
        
        def it_gets_database_is_set_up_no(
                        sqnotes_real : SQNotes
                        ):
            initial_globals = sqnotes_real._get_initial_globals_from_config()
            assert initial_globals['database_is_set_up'] == 'no'
            

    
            
    