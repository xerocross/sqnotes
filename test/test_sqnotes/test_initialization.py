
import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes.configuration_module import ConfigurationModule
from sqnotes.command_validator import CommandValidator
from test.test_helper import do_nothing, get_true

def describe_sqnotes_initialization():
    
    
    def describe_sets_notes_path_without_error():
    
        @patch.object(SQNotes, 'prompt_for_user_notes_path', lambda x: 'notes_path')
        @patch.object(CommandValidator, 'verify_command', get_true)
        @patch.object(ConfigurationModule, 'set_setting_to_user_config', do_nothing)
        @patch.object(ConfigurationModule, 'set_global_to_user_config')
        def it_sets_user_config_global_initialized(
                                                    mock_set_global_to_config,
                                                    sqnotes_obj : SQNotes):
            sqnotes_obj.initialize()
            mock_set_global_to_config.assert_called_once_with(key = 'initialized', value = 'yes')