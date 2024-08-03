
import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes.user_configuration_helper import UserConfigurationHelper
from test.test_helper import just_return


def describe_sqnotes():
    
    
    
    
    def describe_setup_user_configuration():
        
        @patch.object(SQNotes, '_get_user_config_dir', just_return('some/path'))
        @patch.object(UserConfigurationHelper, 'open_or_create_and_open_user_config_file')
        def it_calls_user_config_helper_open_or_create_with_initial_globals(
                                                                        mock_open_or_create_and_open_user_config,
                                                                        sqnotes_obj : SQNotes,
                                                                        test_configuration_dir
                                                                        ):
            
            sqnotes_obj._INITIAL_SETTINGS = None
            sqnotes_obj._INITIAL_GLOBALS = {
                'feature' : 'yes'
            }
            sqnotes_obj.CONFIG_DIR = test_configuration_dir
            sqnotes_obj._setup_user_configuration()
            first_call_args = mock_open_or_create_and_open_user_config.call_args
            _, kwargs = first_call_args
            assert kwargs['initial_globals'] == sqnotes_obj._INITIAL_GLOBALS
            
        @patch.object(SQNotes, '_get_user_config_dir', just_return('some/path'))
        @patch.object(UserConfigurationHelper, 'open_or_create_and_open_user_config_file')
        def it_calls_user_config_helper_open_or_create_with_initial_settings(
                                                                        mock_open_or_create_and_open_user_config,
                                                                        sqnotes_obj : SQNotes,
                                                                        test_configuration_dir
                                                                        ):
            
            sqnotes_obj._INITIAL_GLOBALS = None
            sqnotes_obj._INITIAL_SETTINGS = {
                'feature' : 'yes'
            }
            sqnotes_obj.CONFIG_DIR = test_configuration_dir
            sqnotes_obj._setup_user_configuration()
            first_call_args = mock_open_or_create_and_open_user_config.call_args
            _, kwargs = first_call_args
            assert kwargs['initial_settings'] == sqnotes_obj._INITIAL_SETTINGS
            
        @patch.object(SQNotes, '_get_user_config_dir')
        @patch.object(UserConfigurationHelper, '_set_config_dir')
        @patch.object(UserConfigurationHelper, 'open_or_create_and_open_user_config_file')
        def it_gets_user_config_dir_and_passes_into_user_config_helper(
                                                                        mock_open_or_create_and_open_user_config,
                                                                        mock_set_config_dir,
                                                                        mock_get_user_config_dir,
                                                                        sqnotes_obj : SQNotes
                                                                    ):
            test_config_dir = '/some/path'
            mock_get_user_config_dir.return_value = test_config_dir
            sqnotes_obj._setup_user_configuration()
            mock_set_config_dir.assert_called_once_with(config_dir = test_config_dir)
            
            
        