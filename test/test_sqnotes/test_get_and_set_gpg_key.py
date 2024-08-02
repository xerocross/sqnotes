
from unittest.mock import patch
import pytest
from sqnotes.sqnotes_module import SQNotes, GPG_KEY_EMAIL_KEY
from test.test_helper import get_all_mocked_print_output, do_nothing
from sqnotes.user_configuration_helper import UserConfigurationHelper
from sqnotes import interface_copy


def describe_sqnotes_set_gpg_key_method():

    @patch.object(UserConfigurationHelper, 'set_setting_to_user_config')
    def it_sets_config_data(mock_set_settings_in_user_config,
                                          sqnotes_obj):
        test_gpg_key = 'test@test.com'
        sqnotes_obj.set_gpg_key_email(new_gpg_key_email=test_gpg_key)
        mock_set_settings_in_user_config.assert_called_once_with(key='gpg_key_email', value=test_gpg_key)
        
    
    @patch.object(UserConfigurationHelper, 'set_setting_to_user_config', do_nothing)
    @patch('builtins.print')
    def it_prints_success_message(mocked_print,
                                    sqnotes_obj):
        test_gpg_key = 'test@test.com'
        sqnotes_obj.set_gpg_key_email(new_gpg_key_email=test_gpg_key)
        output = get_all_mocked_print_output(mocked_print=mocked_print)
        assert 'GPG Key set to' in output
    
    
def describe_get_gpg_key_email():
    
    @patch.object(UserConfigurationHelper, 'get_setting_from_user_config')
    def it_calls_config_module_to_get_key(
                                        mock_get_setting_from_user_config,
                                        sqnotes_obj: SQNotes,
                                        
                                        ):
        mock_get_setting_from_user_config.return_value = 'yes'
        result = sqnotes_obj.get_gpg_key_email()
        mock_get_setting_from_user_config.assert_called_once_with(key = GPG_KEY_EMAIL_KEY)
        assert result == 'yes'
        
    
    
def describe_check_gpg_key_email():

    
    def describe_gpg_key_email_is_not_set():
        
        @patch.object(UserConfigurationHelper, 'get_setting_from_user_config')
        def it_exits( mock_get_setting_from_user_config,
                      sqnotes_obj: SQNotes):
            mock_get_setting_from_user_config.return_value = None
            with pytest.raises(SystemExit):
                sqnotes_obj.check_gpg_key_email()
    
        @patch('builtins.print')
        @patch.object(UserConfigurationHelper, 'get_setting_from_user_config')
        def it_prints_gpg_key_not_set_error_message( mock_get_setting_from_user_config,
                                                    mock_print,
                                                    sqnotes_obj: SQNotes
                                                    ):
            mock_get_setting_from_user_config.return_value = None
            with pytest.raises(SystemExit):
                sqnotes_obj.check_gpg_key_email()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            expected_message = interface_copy.GPG_KEY_NOT_SET_MESSAGE()
            assert expected_message in output
    