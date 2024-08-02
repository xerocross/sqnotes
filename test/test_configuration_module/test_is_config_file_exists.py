
import pytest
from unittest.mock import patch
from sqnotes.user_configuration_helper import UserConfigurationHelper

def describe_user_configuration_helper():
    
    def describe_is_config_file_exists():
        
        def describe_config_file_does_exist():
            
            @patch('os.path.exists', lambda x : True)
            def it_returns_true(user_configuration_helper : UserConfigurationHelper):
                is_config_file_exists = user_configuration_helper.is_config_file_exists()
                assert is_config_file_exists == True
                
        def describe_config_file_does_not_exist():
            
            @patch('os.path.exists', lambda x : False)
            def it_returns_false(user_configuration_helper : UserConfigurationHelper):
                is_config_file_exists = user_configuration_helper.is_config_file_exists()
                assert is_config_file_exists == False