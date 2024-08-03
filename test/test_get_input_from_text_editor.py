
from unittest.mock import patch, mock_open
import pytest
from sqnotes.sqnotes_module import SQNotes
from sqnotes.custom_exceptions import TextEditorSubprocessException


TEXT_EDITOR = 'vim'
MOCK_NOTE_CONTENT = 'mock content'


def describe_get_input_from_text_editor():
    
    @pytest.mark.usefixtures('mock_NamedTemporaryFile',
                             'mock_builtin_open')
    def it_calls_subprocess_with_correct_temp_filename (
                                                        sqnotes_obj :SQNotes, 
                                                        mock_subprocess_call,
                                                        mock_temp_file
                                                        ):
        
    
        mock_subprocess_call.return_value = 0  # Simulate successful call
        sqnotes_obj._get_input_from_text_editor(TEXT_EDITOR=TEXT_EDITOR)
        mock_subprocess_call.assert_called_once()
        call_args_list = mock_subprocess_call.call_args_list
        first_called_args, _ = call_args_list[0]
        passed_gpg_command = first_called_args[0]
        argument_in_filename_position = passed_gpg_command[1]
        assert argument_in_filename_position == mock_temp_file.name
        
        
    @pytest.mark.usefixtures('mock_NamedTemporaryFile',
                             'mock_delete_temp_file')
    def it_returns_content_from_text_editor(
                                                sqnotes_obj :SQNotes,
                                                mock_subprocess_call
                                            ):

        mock_open_function = mock_open(read_data = MOCK_NOTE_CONTENT)
        with patch('builtins.open', mock_open_function):
            mock_subprocess_call.return_value = 0  # Simulate successful call
            note_content = sqnotes_obj._get_input_from_text_editor(TEXT_EDITOR=TEXT_EDITOR)
            print(note_content)
            assert note_content == MOCK_NOTE_CONTENT
        
        
    def describe_gpg_subprocess_raises_exception():
        
        @pytest.mark.usefixtures('mock_NamedTemporaryFile',
                                 'mock_delete_temp_file')
        def it_raises_exception (
                                sqnotes_obj,
                                mock_subprocess_call, 
                             ):
    
    
            mock_subprocess_call.side_effect = Exception()
            with pytest.raises(TextEditorSubprocessException):
                sqnotes_obj._get_input_from_text_editor(TEXT_EDITOR = TEXT_EDITOR)
        
    def describe_gpg_returns_error_code():
        
        @pytest.mark.usefixtures('mock_NamedTemporaryFile',
                                 'mock_delete_temp_file')
        def it_raises_exception(
                                sqnotes_obj,
                                mock_subprocess_call, 
                            ):
    
            mock_subprocess_call.return_value = 1
            with pytest.raises(TextEditorSubprocessException):
                sqnotes_obj._get_input_from_text_editor(TEXT_EDITOR=TEXT_EDITOR)

        
        