

from sqnotes.sqnotes_module import SQNotes

import pytest
import os

from unittest.mock import patch



def describe_sqnotes_integration():

    def describe_new_note_method():
        
        
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_open_database",
            "mock_extract_and_save_keywords",
            "mock_insert_new_note_into_database",
            "mock_commit_transaction",
            "mock_NamedTemporaryFile_real"
        )
        def it_creates_a_new_note_in_notes_dir(
                            sqnotes_real : SQNotes,
                            mock_get_input_from_text_editor,
                            sqnotes_config_data,
                            user_config_data,
                            mock_get_new_note_name,
                            gpg_subprocess_call,
                            temp_note_file,
                            test_temp_notes_dir
                            ):
            test_note_content = "test note content"
            mock_get_input_from_text_editor.return_value = test_note_content
            notes_dir = sqnotes_config_data['DEFAULT_NOTES_DIR']
            test_gpg_key_email = 'test@test.com'
            user_config_data['global'] = {
                'initialized' : 'yes',
                'database_is_set_up' : 'yes'
            }
            user_config_data['settings'] = {
                'armor' : 'yes',
                'gpg_key_email': test_gpg_key_email,
                'text_editor' : 'vim',
                'notes_path' : notes_dir
            }
            new_note_name = "test.txt.gpg"
            mock_get_new_note_name.side_effect = [new_note_name]
            sqnotes_real.new_note()
            
            expected_new_note_path = os.path.join(notes_dir, new_note_name)
            print(f"path: {expected_new_note_path}")
            gpg_subprocess_call.assert_called()
            _, kwargs = gpg_subprocess_call.call_args
            in_commands = kwargs['in_commands']
            assert in_commands['infile'] == temp_note_file.name
            assert in_commands['output_path'] == expected_new_note_path
            assert in_commands['GPG_KEY_EMAIL'] == test_gpg_key_email
            