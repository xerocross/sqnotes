import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes import interface_copy
from test.test_helper import get_all_mocked_print_output_to_string



def describe_edit_note():

    def describe_not_initialized():

        @pytest.mark.usefixtures("mock_get_gpg_key_email",
                                 "mock_check_gpg_key_email",
                                 "mock_get_notes_dir_from_config",
                                 "mock_check_text_editor_is_configured",
                                 "mock_get_configured_text_editor",
                                 "mock_open_database",
                                 "set_test_environment")
        @patch.object(SQNotes, '_get_is_initialized')
        def it_exits(mock_get_is_initialized,
                                     sqnotes_obj: SQNotes):
            test_file_name = ''
            mock_get_is_initialized.return_value = False

            with pytest.raises(SystemExit):
                sqnotes_obj.edit_note(test_file_name)

        @pytest.mark.usefixtures("mock_get_gpg_key_email",
                                 "mock_check_gpg_key_email",
                                 "mock_get_notes_dir_from_config",
                                 "mock_check_text_editor_is_configured",
                                 "mock_get_configured_text_editor",
                                 "mock_open_database",
                                 "set_test_environment")
        @patch.object(SQNotes, '_get_is_initialized')
        def it_prints_not_initialized_message(mock_get_is_initialized,
                                     sqnotes_obj: SQNotes,
                                     mock_print):
            test_file_name = ''
            mock_get_is_initialized.return_value = False

            with pytest.raises(SystemExit):
                sqnotes_obj.edit_note(test_file_name)

            output = get_all_mocked_print_output_to_string(mocked_print = mock_print)
            assert interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE() in output

            

            

