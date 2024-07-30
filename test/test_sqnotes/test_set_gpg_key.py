import unittest
from unittest.mock import patch
import os
import pytest
from sqnotes.sqnotes_module import SQNotes
from injector import Injector
from test.test_helper import get_all_mocked_print_output
from sqnotes.configuration_module import ConfigurationModule


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'

def do_nothing(*args, **kwargs):
    pass

@pytest.fixture()
def sqnotes_obj():
    injector = Injector()
    sqnotes = injector.get(SQNotes)
    yield sqnotes
    
def describe_sqnotes_set_gpg_key_method():

    @patch.object(ConfigurationModule, 'set_setting_to_user_config')
    def it_sets_config_data(mock_set_settings_in_user_config,
                                          sqnotes_obj):
        test_gpg_key = 'test@test.com'
        sqnotes_obj.set_gpg_key_email(new_gpg_key_email=test_gpg_key)
        mock_set_settings_in_user_config.assert_called_once_with(key='gpg_key_email', value=test_gpg_key)
        
    
    @patch.object(ConfigurationModule, 'set_setting_to_user_config', do_nothing)
    @patch('builtins.print')
    def it_prints_success_message(mocked_print,
                                    sqnotes_obj):
        test_gpg_key = 'test@test.com'
        sqnotes_obj.set_gpg_key_email(new_gpg_key_email=test_gpg_key)
        output = get_all_mocked_print_output(mocked_print=mocked_print)
        assert 'GPG Key set to' in output
    
    