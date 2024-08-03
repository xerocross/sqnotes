
import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes.user_configuration_helper import UserConfigurationHelper
from test.test_helper import just_return


def describe_sqnotes():
    
    
    
    
    def describe_setup_user_configuration():
        
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
         
        
        @patch.object(SQNotes, '_get_initial_user_settings_from_config')
        @patch.object(UserConfigurationHelper, 'open_or_create_and_open_user_config_file')
        def it_passes_init_globals_from_config_to_open_or_create_user_config(
                                                         mock_open_or_create_and_open_user_config,
                                                         mock_get_initial_user_settings_from_config,
                                                         sqnotes_obj : SQNotes,
                                                         mock_get_initial_globals_from_config,
                                                         mock_get_user_config_dir
                                                                            ):
            
            init_globals = {
                'initialized' : 'no',
                'database_is_set_up' : 'no'
            }
            mock_get_initial_user_settings_from_config.return_value = {}
            mock_get_initial_globals_from_config.return_value = init_globals
            
            sqnotes_obj._setup_user_configuration()
            mock_open_or_create_and_open_user_config.assert_called()
            _, kwargs = mock_open_or_create_and_open_user_config.call_args_list[0]
            assert kwargs['initial_globals'] == init_globals
            
        @pytest.mark.usefixtures("mock_get_user_config_dir")
        @patch.object(SQNotes, '_get_initial_user_settings_from_config')
        @patch.object(UserConfigurationHelper, 'open_or_create_and_open_user_config_file')
        def it_passes_init_user_settings_from_config_to_open_or_create_user_config(
                                                         mock_open_or_create_and_open_user_config,
                                                         mock_get_initial_user_settings_from_config,
                                                         sqnotes_obj : SQNotes,
                                                         mock_get_initial_globals_from_config
                                                                            ):
            
            init_user_settings = {
                'use-ascii-armor' : 'no',
            }
            mock_get_initial_globals_from_config.return_value = {}
            mock_get_initial_user_settings_from_config.return_value = init_user_settings
            
            sqnotes_obj._setup_user_configuration()
            mock_open_or_create_and_open_user_config.assert_called()
            _, kwargs = mock_open_or_create_and_open_user_config.call_args_list[0]
            assert kwargs['initial_settings'] == init_user_settings
            
    def describe_get_initial_globals_from_config():
        
        def it_reads_init_globals_from_config (
                                                sqnotes_obj : SQNotes,
                                                mock_config_data
                                            ):
            configured_init_globals = {
                'initialized' : 'no',
                'database_is_set_up' : 'no'
            }
            mock_config_data['INIT_GLOBALS'] = configured_init_globals
            resulting_init_globals = sqnotes_obj._get_initial_globals_from_config()
            for key in configured_init_globals:
                assert resulting_init_globals[key] == configured_init_globals[key]
            
    def describe_get_initial_user_settings_from_config():
        
        def it_reads_init_user_settings_from_config(
                                                sqnotes_obj : SQNotes,
                                                mock_config_data
                                                ):
            configured_init_settings = {
                'use-ascii-armor' : 'no',
                'something-else' : 'yes'
            }
            mock_config_data['INIT_USER_SETTINGS'] = configured_init_settings
            resulting_init_settings = sqnotes_obj._get_initial_user_settings_from_config()
            for key in resulting_init_settings:
                assert resulting_init_settings[key] == configured_init_settings[key]
            
    