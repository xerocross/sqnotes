
import pytest
from sqnotes.sqnotes_module import SQNotes


TEXT_EDITOR = 'vim'

def describe_get_edited_note_from_editor():
    
    @pytest.mark.usefixtures("mock_builtin_open")
    def it_opens_editor(
                        mock_subprocess_run,
                        sqnotes_obj : SQNotes,
                        mock_get_configured_text_editor,
                        mock_subprocess_result
                    ):
        
        mock_get_configured_text_editor.return_value = TEXT_EDITOR
        mock_subprocess_result.returncode = 0
        temp_filename = "temp.txt"
        sqnotes_obj._get_edited_note_from_text_editor(temp_filename)
        mock_subprocess_run.assert_called_once()
        called_args, _ = mock_subprocess_run.call_args
        assert called_args[0][0] == TEXT_EDITOR
        
    @pytest.mark.usefixtures("mock_builtin_open")
    def it_opens_editor_with_tempfile_name(
                                        mock_subprocess_run,
                                        mock_get_configured_text_editor,
                                        sqnotes_obj : SQNotes,
                                        mock_subprocess_result
                                    ):
        mock_get_configured_text_editor.return_value = TEXT_EDITOR
        mock_subprocess_result.returncode = 0
        temp_filename = "temp.txt"
        
        sqnotes_obj._get_edited_note_from_text_editor(temp_filename)
        
        mock_subprocess_run.assert_called_once()
        called_args, _ = mock_subprocess_run.call_args
        assert called_args[0][1] == temp_filename

    