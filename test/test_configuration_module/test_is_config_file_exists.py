
import pytest
from unittest.mock import patch
from sqnotes.configuration_module import ConfigurationModule

def describe_configuration_module():
    
    def describe_is_config_file_exists():
        
        def describe_config_file_does_exist():
            
            @patch('os.path.exists', lambda x : True)
            def it_returns_true(configuration_module : ConfigurationModule):
                is_config_file_exists = configuration_module.is_config_file_exists()
                assert is_config_file_exists == True
                
        def describe_config_file_does_not_exist():
            
            @patch('os.path.exists', lambda x : False)
            def it_returns_false(configuration_module : ConfigurationModule):
                is_config_file_exists = configuration_module.is_config_file_exists()
                assert is_config_file_exists == False