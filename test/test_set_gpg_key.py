import unittest
from unittest.mock import patch
import os
import pytest
from sqnotes import SQNotes


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'

class TestSQNotesSetGPGKey(unittest.TestCase):
    
    def setUp(self):
        self.sqnotes = SQNotes()
        
        
    @patch.object(SQNotes, '_set_setting_in_user_config')
    def test_set_gpg_key_sets_config_data(self,
                                          mock_set_settings_in_user_config):
        test_gpg_key = 'test@test.com'
        self.sqnotes.set_gpg_key_email(new_gpg_key_email=test_gpg_key)
        mock_set_settings_in_user_config.assert_called_once_with(key='gpg_key_email', value=test_gpg_key)
        
    
    @patch.object(SQNotes, '_set_setting_in_user_config')
    @patch('builtins.print')
    def test_prints_success_message(self,
                                    mocked_print,
                                    mock_set_settings_in_user_config):
        test_gpg_key = 'test@test.com'
        self.sqnotes.set_gpg_key_email(new_gpg_key_email=test_gpg_key)
        args, _ = mocked_print.call_args
        printed_text = args[0]
        self.assertIn('GPG Key set to', printed_text)
        