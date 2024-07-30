
from unittest.mock import patch
import os
import pytest
from sqnotes.configuration_module import ConfigurationModule
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    

def describe_the_configuration_module():

    def it_sets_and_gets_config_user_settings(
                                    configuration_module : ConfigurationModule
                                    ):
        configuration_module.open_or_create_and_open_user_config_file()
        key = 'my_key'
        value = 'apple'
        configuration_module.set_setting_to_user_config(key=key, value=value)
        assert configuration_module.get_setting_from_user_config(key = key) == value
        
        
    def it_sets_and_gets_config_global_settings(
                                    configuration_module : ConfigurationModule
                                    ):
        configuration_module.open_or_create_and_open_user_config_file()
        key = 'my_key'
        value = 'apple'
        configuration_module.set_global_to_user_config(key=key, value=value)
        assert configuration_module.get_global_from_user_config(key = key) == value
        
    def it_returns_null_on_get_unknown_setting_key(
                                            configuration_module : ConfigurationModule
                                                ):
        configuration_module.open_or_create_and_open_user_config_file()
        value = configuration_module.get_setting_from_user_config(key='unknown')
        assert value == None
        
        
    def it_returns_null_on_get_unknown_global_key(
                                            configuration_module : ConfigurationModule
                                                ):
        configuration_module.open_or_create_and_open_user_config_file()
        value = configuration_module.get_global_from_user_config(key='unknown')
        assert value == None
        
    

    
    