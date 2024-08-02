
from unittest.mock import patch
import os
import pytest
from sqnotes.user_configuration_helper import UserConfigurationHelper
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    

def describe_the_user_configuration_helper():

    def it_sets_and_gets_config_user_settings(
                                    user_configuration_helper : UserConfigurationHelper
                                    ):
        user_configuration_helper.open_or_create_and_open_user_config_file()
        key = 'my_key'
        value = 'apple'
        user_configuration_helper.set_setting_to_user_config(key=key, value=value)
        assert user_configuration_helper.get_setting_from_user_config(key = key) == value
        
        
    def it_sets_and_gets_config_global_settings(
                                    user_configuration_helper : UserConfigurationHelper
                                    ):
        user_configuration_helper.open_or_create_and_open_user_config_file()
        key = 'my_key'
        value = 'apple'
        user_configuration_helper.set_global_to_user_config(key=key, value=value)
        assert user_configuration_helper.get_global_from_user_config(key = key) == value
        
    def it_returns_null_on_get_unknown_setting_key(
                                            user_configuration_helper : UserConfigurationHelper
                                                ):
        user_configuration_helper.open_or_create_and_open_user_config_file()
        value = user_configuration_helper.get_setting_from_user_config(key='unknown')
        assert value == None
        
        
    def it_returns_null_on_get_unknown_global_key(
                                            user_configuration_helper : UserConfigurationHelper
                                                ):
        user_configuration_helper.open_or_create_and_open_user_config_file()
        value = user_configuration_helper.get_global_from_user_config(key='unknown')
        assert value == None
        
    

    
    