
import pytest
from unittest.mock import patch
from test.test_fixtures import sqnotes_obj, test_temporary_directory
from sqnotes.sqnotes_module import SQNotes
from sqnotes.configuration_module import ConfigurationModule


def describe_sqnotes():
    
    def describe_setup_user_configuration():
        
        
        @patch.object(ConfigurationModule, 'open_or_create_and_open_user_config_file')
        def it_calls_config_module_open_or_create_with_initial_globals(
                                                                        mock_open_or_create_and_open_user_config,
                                                                        sqnotes_obj : SQNotes,
                                                                        test_temporary_directory
                                                                        ):
            
            sqnotes_obj._INITIAL_SETTINGS = None
            sqnotes_obj._INITIAL_GLOBALS = {
                'feature' : 'yes'
            }
            sqnotes_obj.CONFIG_DIR = test_temporary_directory
            sqnotes_obj._setup_user_configuration()
            first_call_args = mock_open_or_create_and_open_user_config.call_args
            _, kwargs = first_call_args
            assert kwargs['initial_globals'] == sqnotes_obj._INITIAL_GLOBALS
            
        @patch.object(ConfigurationModule, 'open_or_create_and_open_user_config_file')
        def it_calls_config_module_open_or_create_with_initial_settings(
                                                                        mock_open_or_create_and_open_user_config,
                                                                        sqnotes_obj : SQNotes,
                                                                        test_temporary_directory
                                                                        ):
            
            sqnotes_obj._INITIAL_GLOBALS = None
            sqnotes_obj._INITIAL_SETTINGS = {
                'feature' : 'yes'
            }
            sqnotes_obj.CONFIG_DIR = test_temporary_directory
            sqnotes_obj._setup_user_configuration()
            first_call_args = mock_open_or_create_and_open_user_config.call_args
            _, kwargs = first_call_args
            assert kwargs['initial_settings'] == sqnotes_obj._INITIAL_SETTINGS
            
            
        