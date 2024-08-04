

from sqnotes.sqnotes_module import SQNotes

import pytest
import os

from unittest.mock import patch
from conftest import test_temp_notes_dir
from sqnotes.encrypted_note_helper import EncryptedNoteHelper


@pytest.fixture
def sqnotes_with_real_data_in_memory_setup(
                                    sqnotes_real : SQNotes,
                                    user_config_data,
                                    test_temp_notes_dir
                                ):
    user_config_data['global']['initialized'] = 'yes'
    user_config_data['global'][sqnotes_real.DATABASE_IS_SET_UP_KEY] = 'no'
    user_config_data['settings'].update({
                'armor' : 'yes',
                'gpg_key_email': 'test@test.com',
                'text_editor' : 'vim',
                'notes_path' : test_temp_notes_dir
            })
    yield sqnotes_real
    

def describe_sqnotes_integration():

    def describe_new_note_method():
        
        
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_NamedTemporaryFile_real"
        )
        def it_creates_a_new_note_in_notes_dir (
                            sqnotes_with_real_data_in_memory_setup : SQNotes,
                            mock_get_input_from_text_editor,
                            mock_get_new_note_name,
                            mock_call_gpg_subprocess_to_write_encrypted,
                            temp_note_file,
                            test_temp_notes_dir
                            ):
            test_note_content = "test note content"
            mock_get_input_from_text_editor.return_value = test_note_content
            
            new_note_name = "test.txt.gpg"
            mock_get_new_note_name.side_effect = [new_note_name]
            sqnotes_with_real_data_in_memory_setup.new_note()
            
            expected_new_note_path = os.path.join(test_temp_notes_dir, new_note_name)
            print(f"path: {expected_new_note_path}")
            mock_call_gpg_subprocess_to_write_encrypted.assert_called()
            _, kwargs = mock_call_gpg_subprocess_to_write_encrypted.call_args
            in_commands = kwargs['in_commands']
            assert in_commands['infile'] == temp_note_file.name
            assert in_commands['output_path'] == expected_new_note_path
            assert in_commands['GPG_KEY_EMAIL'] == 'test@test.com'
            
            
    @pytest.fixture
    def mock_decrypt_note_into_temp_file(temp_note_file):
        
        def mock_decrypt_into_temp(_, note_path):
            decrypted_note_path = str(temp_note_file.name)
            with open(decrypted_note_path, 'w') as file:
                file.write('decrypted note content')
            return decrypted_note_path
        
        with patch.object(EncryptedNoteHelper, 'decrypt_note_into_temp_file', mock_decrypt_into_temp) as mock:
            yield mock
            
        
    #
    #
    # def describe_edit_note_method():
    #
    #     @pytest.mark.usefixtures(
    #         "mock_check_gpg_verified",
    #         "mock_commit_transaction",
    #         "mock_NamedTemporaryFile_real",
    #         "mock_get_note_id_or_raise",
    #     )
    #     def it_writes_new_note_with_edited_content(
    #                                         sqnotes_real_data_in_memory_setup : SQNotes,
    #                                         sqnotes_config_data,
    #                                         user_config_data,
    #                                         temp_note_file,
    #                                         test_temp_notes_dir,
    #                                         mock_decrypt_note_into_temp_file,
    #                                         mock_get_edited_note_content,
    #                                         mock_call_gpg_subprocess_to_write_encrypted
    #                                         ):
    #         test_note_content = "test note content"
    #         note_base_name = "note1.txt"
    #         note_path = str(test_temp_notes_dir / note_base_name)
    #         with open(note_path, 'w') as file:
    #             file.write(test_note_content)
    #         mock_get_edited_note_content.return_value = "edited_content"
    #         test_gpg_key_email = 'test@test.com'
    #
    #         sqnotes_real_data_in_memory_setup.edit_note(filename=note_base_name)
    #         mock_call_gpg_subprocess_to_write_encrypted.assert_called()
    #         _, kwargs = mock_call_gpg_subprocess_to_write_encrypted.call_args
    #         in_commands = kwargs['in_commands']
    #
    #         assert in_commands['infile'] == temp_note_file.name
    #         assert in_commands['output_path'] == note_path
    #         assert in_commands['GPG_KEY_EMAIL'] == test_gpg_key_email
    #
    #
    #

        
            