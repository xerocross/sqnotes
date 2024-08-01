import pytest
from sqnotes.sqnotes_module import SQNotes
from unittest.mock import patch
from test.test_helper import do_nothing, just_return, get_all_mocked_print_output
from sqnotes.database_service import DatabaseService
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from sqnotes import interface_copy



@pytest.fixture
def mock_get_is_initialized_false():
    with patch.object(SQNotes, '_get_is_initialized') as mock:
        mock.return_value = False
        yield mock

def describe_new_note():

    def describe_not_initialized():

        @pytest.mark.usefixtures('mock_get_is_initialized_false', 
                                 'set_test_environment')
        @patch.object(SQNotes,'_is_use_ascii_armor', lambda x: True)
        @patch.object(SQNotes,'_get_configured_text_editor', lambda x: 'vim')
        @patch.object(SQNotes, 'check_text_editor_is_configured', do_nothing)
        @patch.object(DatabaseService, 'commit_transaction', do_nothing)
        @patch.object(SQNotes, '_extract_and_save_keywords', do_nothing)
        @patch.object(DatabaseService, 'insert_new_note_into_database', do_nothing)
        @patch.object(SQNotes, '_check_gpg_verified', do_nothing)
        @patch.object(SQNotes, 'check_gpg_key_email', lambda x: True)
        @patch.object(EncryptedNoteHelper, 'write_encrypted_note', just_return('test_note'))
        @patch.object(SQNotes, '_get_new_note_name', just_return("test.txt.gpg"))
        @patch.object(SQNotes, 'get_gpg_key_email', just_return('test@test.com'))
        @patch.object(SQNotes, 'get_notes_dir_from_config', just_return('notes/path'))
        def it_prints_must_initialized_message(sqnotes_obj: SQNotes,
                                               mock_print):
            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()
                output = get_all_mocked_print_output(mocked_print = mock_print)
                assert interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE() in output



        @pytest.mark.usefixtures('mock_get_is_initialized_false', 
                                        'set_test_environment')
        @patch.object(SQNotes,'_is_use_ascii_armor', lambda x: True)
        @patch.object(SQNotes,'_get_configured_text_editor', lambda x: 'vim')
        @patch.object(SQNotes, 'check_text_editor_is_configured', do_nothing)
        @patch.object(DatabaseService, 'commit_transaction', do_nothing)
        @patch.object(SQNotes, '_extract_and_save_keywords', do_nothing)
        @patch.object(DatabaseService, 'insert_new_note_into_database', do_nothing)
        @patch.object(SQNotes, '_check_gpg_verified', do_nothing)
        @patch.object(SQNotes, 'check_gpg_key_email', lambda x: True)
        @patch.object(EncryptedNoteHelper, 'write_encrypted_note', just_return('test_note'))
        @patch.object(SQNotes, '_get_new_note_name', just_return("test.txt.gpg"))
        @patch.object(SQNotes, 'get_gpg_key_email', just_return('test@test.com'))
        @patch.object(SQNotes, 'get_notes_dir_from_config', just_return('notes/path'))
        def it_exits(sqnotes_obj: SQNotes,
                                    mock_print):
            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()

