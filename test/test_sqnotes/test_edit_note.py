

import pytest
from unittest.mock import Mock, patch
from sqnotes.sqnotes_module import SQNotes

from test.test_helper import do_nothing, get_all_mocked_print_output
from sqnotes.encrypted_note_helper import GPGSubprocessException
from sqnotes import interface_copy



    
def describe_edit_note():
    
    
    def describe_note_file_not_found():
        
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file")
        
        def it_exits (
                                            sqnotes_obj,
                                            test_note_file,
                                            test_note_filename,
                                            mock_exists,
                                            mock_decrypt_note_into_temp_file,
                                            test_note_temp_file,
                                            mock_get_edited_note_content,
                                            mock_get_note_id_or_raise
                                        ):
            mock_exists.return_value = False
            mock_decrypt_note_into_temp_file.return_value = test_note_temp_file
            mock_get_edited_note_content.return_value = "edited test content"
            mock_get_note_id_or_raise.return_value = 1
            with pytest.raises(SystemExit):
                sqnotes_obj.edit_note(filename=test_note_file)
            
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file")
        
        @patch('builtins.print')
        def it_prints_note_not_found_error (
                                            mock_print,
                                            sqnotes_obj,
                                            test_note_file,
                                            test_note_filename,
                                            mock_exists,
                                            mock_decrypt_note_into_temp_file,
                                            test_note_temp_file,
                                            mock_get_edited_note_content,
                                            mock_get_note_id_or_raise
                                        ):
            mock_exists.return_value = False
            mock_decrypt_note_into_temp_file.return_value = test_note_temp_file
            mock_get_edited_note_content.return_value = "edited test content"
            mock_get_note_id_or_raise.return_value = 1
            with pytest.raises(SystemExit):
                sqnotes_obj.edit_note(filename=test_note_file)
            output = get_all_mocked_print_output(mocked_print = mock_print)
            expected_message = interface_copy.NOTE_NOT_FOUND_ERROR().format(test_note_file)
            exiting_message = interface_copy.EXITING()
            assert expected_message in output
            assert exiting_message in output
    
    
    
    def describe_happy_path():
    
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file")
        def it_executes_without_throwing(
                                            sqnotes_obj,
                                            test_note_file,
                                            test_note_filename,
                                            mock_exists,
                                            mock_decrypt_note_into_temp_file,
                                            test_note_temp_file,
                                            mock_get_edited_note_content,
                                            mock_get_note_id_or_raise
                                        ):
            mock_exists.return_value = True
            mock_decrypt_note_into_temp_file.return_value = test_note_temp_file
            mock_get_edited_note_content.return_value = "edited test content"
            mock_get_note_id_or_raise.return_value = 1
            try:
                sqnotes_obj.edit_note(filename=test_note_file)
            except Exception as e:
                pytest.fail(f"exception {e}")
                
                
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file")
        def it_calls_to_decrypt_note (
                                            sqnotes_obj,
                                            test_note_file,
                                            test_note_filename,
                                            mock_exists,
                                            mock_decrypt_note_into_temp_file,
                                            test_note_temp_file,
                                            mock_get_edited_note_content,
                                            mock_get_note_id_or_raise
                                        ):
            mock_exists.return_value = True
            mock_decrypt_note_into_temp_file.return_value = test_note_temp_file
            mock_get_edited_note_content.return_value = "edited test content"
            mock_get_note_id_or_raise.return_value = 1
            sqnotes_obj.edit_note(filename=test_note_file)
            mock_decrypt_note_into_temp_file.assert_called_once()
            _, called_kwargs = mock_decrypt_note_into_temp_file.call_args
            assert called_kwargs['note_path'] == test_note_file
                
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file")
        def it_calls_write_function_with_content_from_editor(
                                                            sqnotes_obj,
                                                            test_note_file,
                                                            test_note_filename,
                                                            mock_exists,
                                                            mock_decrypt_note_into_temp_file,
                                                            test_note_temp_file,
                                                            mock_get_edited_note_content,
                                                            mock_get_note_id_or_raise,
                                                            mock_write_encrypted_note
                                                            ):
            mock_exists.return_value = True
            mock_decrypt_note_into_temp_file.return_value = test_note_temp_file
            test_content = "edited test content"
            mock_get_edited_note_content.return_value = test_content
            mock_get_note_id_or_raise.return_value = 1
            sqnotes_obj.edit_note(filename=test_note_file)
            mock_write_encrypted_note.assert_called_once_with(note_file_path=test_note_file,note_content=test_content)
                
                
    def describe_if_decryption_raises_gpg_subprocess_exception():
        
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file")
        def it_exits(
                        sqnotes_obj,
                        test_note_file,
                        test_note_filename,
                        mock_exists,
                        mock_decrypt_note_into_temp_file,
                        test_note_temp_file,
                        mock_get_edited_note_content,
                        mock_get_note_id_or_raise
                        ):
            mock_exists.return_value = True
            mock_decrypt_note_into_temp_file.side_effect = GPGSubprocessException()
            with pytest.raises(SystemExit):
                sqnotes_obj.edit_note(filename=test_note_file)
                
                
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file")
        @patch('builtins.print')
        def it_prints_gpg_error_message(
                                    mock_print,
                                    sqnotes_obj,
                                    test_note_file,
                                    test_note_filename,
                                    mock_exists,
                                    mock_decrypt_note_into_temp_file,
                                    test_note_temp_file,
                                    mock_get_edited_note_content,
                                    mock_get_note_id_or_raise
                                    ):
            mock_exists.return_value = True
            mock_decrypt_note_into_temp_file.side_effect = GPGSubprocessException()
            with pytest.raises(SystemExit):
                sqnotes_obj.edit_note(filename=test_note_file)
            output = get_all_mocked_print_output(mocked_print=mock_print)
            expected_message = interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
            exiting_message = interface_copy.EXITING()
            assert expected_message in output
            assert exiting_message in output
        
            
                