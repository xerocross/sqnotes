
import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes.configuration_module import ConfigurationModule
from sqnotes.command_validator import CommandValidator
from test.test_helper import do_nothing, get_true, just_return,\
    get_all_mocked_print_output_to_string
from sqnotes import interface_copy


def describe_sqnotes_initialization():
    
    
    @pytest.fixture
    def mock_prompt_for_user_notes_path ():
        with patch.object(SQNotes, 'prompt_for_user_notes_path') as mock:
            mock.return_value = "notes_path"
            yield mock
    
    
    @pytest.mark.usefixtures("mock_prompt_for_user_notes_path")
    @patch.object(CommandValidator, 'verify_command', get_true)
    @patch.object(ConfigurationModule, 'set_setting_to_user_config', do_nothing)
    @patch.object(ConfigurationModule, 'set_global_to_user_config', do_nothing)
    @patch.object(SQNotes, 'choose_text_editor_interactive')
    def it_calls_to_choose_text_editor_interactively(
                                                    mock_choose_text_editor_interactively,
                                                    sqnotes_obj : SQNotes
                                                    ):
        sqnotes_obj.initialize()
        mock_choose_text_editor_interactively.assert_called_once_with()
        
        
        
    
    def describe_sets_notes_path_without_error():
    
        @patch.object(SQNotes, 'prompt_for_user_notes_path', lambda x: 'notes_path')
        @patch.object(CommandValidator, 'verify_command', get_true)
        @patch.object(ConfigurationModule, 'set_setting_to_user_config', do_nothing)
        @patch.object(SQNotes, 'choose_text_editor_interactive', do_nothing)
        @patch.object(ConfigurationModule, 'set_global_to_user_config')
        def it_sets_user_config_global_to_initialized(
                                                    mock_set_global_to_config,
                                                    sqnotes_obj : SQNotes):
            sqnotes_obj.initialize()
            mock_set_global_to_config.assert_called_once_with(key = 'initialized', value = 'yes')
           
           
        @patch.object(SQNotes, 'prompt_for_user_notes_path', lambda x: 'notes_path')
        @patch.object(CommandValidator, 'verify_command', get_true)
        @patch.object(ConfigurationModule, 'set_setting_to_user_config', do_nothing)
        @patch.object(SQNotes, 'choose_text_editor_interactive', do_nothing)
        @patch.object(ConfigurationModule, 'set_global_to_user_config', do_nothing)
        def it_prints_initialized_message(
                                        sqnotes_obj : SQNotes,
                                        mock_printer_helper_print
                                        ):
            sqnotes_obj.initialize()
            output = get_all_mocked_print_output_to_string(mocked_print=mock_printer_helper_print)
            expected_message = interface_copy.INITIALIZATION_COMPLETE()
            assert expected_message in output
           
           
            
def describe_get_is_initialized():
    
    def describe_initialized_in_config_is_yes():
        
        @patch.object(ConfigurationModule, 'get_global_from_user_config', just_return('yes'))
        def it_returns_true(
                                sqnotes_obj : SQNotes
                            ):
            value = sqnotes_obj._get_is_initialized()
            assert value

    def describe_initialized_in_config_is_none():
        
        @patch.object(ConfigurationModule, 'get_global_from_user_config', just_return(None))
        def it_returns_false(
                                sqnotes_obj : SQNotes
                            ):
            value = sqnotes_obj._get_is_initialized()
            assert not value
