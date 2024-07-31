

from unittest.mock import patch, mock_open, MagicMock, call
import pytest
from sqnotes.sqnotes_module import SQNotes
from test.test_helper import get_all_mocked_print_output, do_nothing,\
    just_return, get_all_mocked_print_output_to_string

from sqnotes.choose_text_editor import ChooseTextEditor,\
    MaxInputAttemptsException
from sqnotes import interface_copy

def side_effect_callable():
    side_effect_callable.called = getattr(side_effect_callable, "called", 0) + 1
    if side_effect_callable.called == 1:
        raise ValueError("Simulated exception")
    else:
        return 0



 
def describe_choose_text_editor_interactive():
    
    @pytest.fixture
    def mock_set_configured_text_editor():
        with patch.object(SQNotes, '_set_configured_text_editor') as mock:
            yield mock
    
    @pytest.fixture
    def mock_get_available_text_editors():
        with patch.object(SQNotes, '_get_available_text_editors') as mock:
            mock.return_value = ['vim', 'nano']
            yield mock
    
    @pytest.fixture
    def mock_get_suported_text_editors():
        with patch.object(SQNotes, '_get_supported_text_editors') as mock:
            mock.return_value = ['vim', 'nano', 'vi']
            yield mock
    
    
    def describe_on_choose_text_editor_object():
    
        @pytest.mark.usefixtures("mock_set_configured_text_editor",
                                 "mock_get_available_text_editors")
        @patch.object(ChooseTextEditor, 'choose_text_editor_interactive', do_nothing)
        @patch.object(ChooseTextEditor, 'set_available_editors')
        def it_sets_available_editors(
                                                    mock_set_available_editors,
                                                    sqnotes_obj : SQNotes
                                                ):
            sqnotes_obj.choose_text_editor_interactive()
            mock_set_available_editors.assert_called_once_with(available_editors = ['vim', 'nano'])
        
        
        @pytest.mark.usefixtures("mock_set_configured_text_editor",
                                 "mock_get_available_text_editors",
                                 "mock_get_suported_text_editors")
        @patch.object(ChooseTextEditor, 'choose_text_editor_interactive', do_nothing)
        @patch.object(ChooseTextEditor, 'set_available_editors', do_nothing)
        @patch.object(ChooseTextEditor, 'set_supported_editors')
        def it_sets_supported_editors(
                                                    mock_set_supported_editors,
                                                    sqnotes_obj : SQNotes
                                                ):
            sqnotes_obj.choose_text_editor_interactive()
            mock_set_supported_editors.assert_called_once_with(supported_editors = ['vim', 'nano', 'vi'])
        
    
    
        @pytest.mark.usefixtures("mock_set_configured_text_editor",
                                 "mock_get_available_text_editors")
        @patch.object(ChooseTextEditor, 'choose_text_editor_interactive')
        def it_calls_choose_editor_method(
                                                    mock_choose_text_editor,
                                                    sqnotes_obj : SQNotes,
                                                    mock_print
                                                ):
            sqnotes_obj.choose_text_editor_interactive()
            mock_choose_text_editor.assert_called_once()
            
            
        def describe_on_gets_valid_user_input():
            
            @pytest.mark.usefixtures("mock_set_configured_text_editor",
                                     "mock_get_available_text_editors",
                                     "mock_get_suported_text_editors")
            @patch.object(ChooseTextEditor, 'choose_text_editor_interactive')
            def it_calls_set_text_editor_config_value(
                                            mock_choose_text_editor,
                                            mock_set_configured_text_editor,
                                            sqnotes_obj : SQNotes,
                                            ):
                chosen_editor = 'vim'
                mock_choose_text_editor.return_value = chosen_editor
                sqnotes_obj.choose_text_editor_interactive()
                mock_set_configured_text_editor.assert_called_once_with(editor = chosen_editor)
        
        
        def describe_choose_text_editor_raises_max_attempts_exception():
            
            @pytest.mark.usefixtures("mock_set_configured_text_editor",
                                     "mock_get_available_text_editors",
                                     "mock_get_suported_text_editors")
            @patch.object(ChooseTextEditor, 'choose_text_editor_interactive')
            def it_prints_an_error_message(
                                            mock_choose_text_editor,
                                            mock_set_configured_text_editor,
                                            sqnotes_obj : SQNotes,
                                            mock_print
                                            ):
                mock_choose_text_editor.side_effect = MaxInputAttemptsException()
                sqnotes_obj.choose_text_editor_interactive()
                
                output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                expected_message = interface_copy.DID_NOT_SET_TEXT_EDITOR_TRY_AGAIN()
                assert expected_message in output
        
    
        
        
    