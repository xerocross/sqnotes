

import pytest
from unittest.mock import Mock, patch
from sqnotes.sqnotes_module import SQNotes

from test.test_helper import do_nothing, get_all_mocked_print_output,\
    just_return, get_all_mocked_print_output_to_string
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
                                 "mock_delete_temp_file",
            "mock_get_is_initialized")
        
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
                                 "mock_delete_temp_file",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
        
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
            output = get_all_mocked_print_output_to_string(mocked_print = mock_print)
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
                                 "mock_delete_temp_file",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
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
                                 "mock_delete_temp_file",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
        def it_calls_to_edit_the_note_created_by_decrypting (
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
            mock_get_edited_note_content.assert_called_once_with(temp_filename=test_note_temp_file)
                
                
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
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
                                 "mock_delete_temp_file",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
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
            mock_write_encrypted_note.assert_called()
            _, call_kwargs = mock_write_encrypted_note.call_args
            assert call_kwargs['note_file_path'] == test_note_file
            assert call_kwargs['note_content'] == test_content
                
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file",
                                 "mock_get_gpg_key_email",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
        def it_passes_gpg_key_email_into_write_function (
                                                            sqnotes_obj,
                                                            test_note_file,
                                                            test_note_filename,
                                                            mock_exists,
                                                            mock_decrypt_note_into_temp_file,
                                                            test_note_temp_file,
                                                            mock_get_edited_note_content,
                                                            mock_get_note_id_or_raise,
                                                            mock_write_encrypted_note,
                                                            mock_get_gpg_key_email
                                                            ):
            gpg_key_email = 'test@test.com'
            mock_get_gpg_key_email.return_value = gpg_key_email
            mock_exists.return_value = True
            mock_decrypt_note_into_temp_file.return_value = test_note_temp_file
            test_content = "edited test content"
            mock_get_edited_note_content.return_value = test_content
            mock_get_note_id_or_raise.return_value = 1
            sqnotes_obj.edit_note(filename=test_note_file)
            call_args = mock_write_encrypted_note.call_args
            _, kwargs = call_args
            passed_config = kwargs['config']
            passed_gpg_key_email = passed_config['GPG_KEY_EMAIL']
            assert passed_gpg_key_email == gpg_key_email
            
            
        def describe_using_ascii_armor():
            
            @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                     "mock_extract_and_save_keywords",
                                     "mock_commit_transaction",
                                     "mock_get_gpg_key_email",
                                     "mock_open_database",
                                     "mock_get_notes_dir_from_config",
                                     "mock_get_configured_text_editor",
                                     "mock_delete_temp_file",
                                     "mock_get_gpg_key_email",
            "mock_get_is_initialized")
            @patch.object(SQNotes, '_is_use_ascii_armor', just_return(True))
            def it_passes_ascii_armor_yes_into_config_into_write_function (
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
                call_args = mock_write_encrypted_note.call_args
                _, kwargs = call_args
                passed_config = kwargs['config']
                passed_ascii_armor_config = passed_config['USE_ASCII_ARMOR']
                assert passed_ascii_armor_config == True
                
        def describe_not_using_ascii_armor():
            
            @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                     "mock_extract_and_save_keywords",
                                     "mock_commit_transaction",
                                     "mock_get_gpg_key_email",
                                     "mock_open_database",
                                     "mock_get_notes_dir_from_config",
                                     "mock_get_configured_text_editor",
                                     "mock_delete_temp_file",
                                     "mock_get_gpg_key_email",
            "mock_get_is_initialized")
            @patch.object(SQNotes, '_is_use_ascii_armor', just_return(False))
            def it_passes_ascii_armor_false_into_config_into_write_function (
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
                call_args = mock_write_encrypted_note.call_args
                _, kwargs = call_args
                passed_config = kwargs['config']
                passed_ascii_armor_config = passed_config['USE_ASCII_ARMOR']
                assert passed_ascii_armor_config == False
                
                
    def describe_if_decryption_raises_gpg_subprocess_exception():
        
        @pytest.mark.usefixtures("mock_delete_keywords_from_database_for_note",
                                 "mock_write_encrypted_note",
                                 "mock_extract_and_save_keywords",
                                 "mock_commit_transaction",
                                 "mock_get_gpg_key_email",
                                 "mock_open_database",
                                 "mock_get_notes_dir_from_config",
                                 "mock_get_configured_text_editor",
                                 "mock_delete_temp_file",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
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
                                 "mock_delete_temp_file",
                                 "mock_is_use_ascii_armor",
            "mock_get_is_initialized")
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
            output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
            expected_message = interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
            exiting_message = interface_copy.EXITING()
            assert expected_message in output
            assert exiting_message in output
        
            
                