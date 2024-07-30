import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
import tempfile
from sqnotes.encrypted_note_helper import EncryptedNoteHelper, GPGSubprocessException
from sqnotes.database_service import DatabaseService
from test.test_helper import get_all_mocked_print_output, do_nothing
from injector import Injector
from sqnotes.sqnotes_module import SQNotes


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
        
class TestSQNotesCreateNewNote(unittest.TestCase):
    open_database_patcher = None
    use_ascii_armor_patcher = None
    gpg_verified_patcher = None
    mock_commit_patcher = None
    check_gpg_key_email_patcher = None
    mock_get_gpg_key_email_patcher = None
    mock_get_notes_dir_from_config_patcher = None
    mock_get_notes_dir_from_config_patcher = None

    @classmethod
    def setUpClass(cls):
        cls.open_database_patcher = patch.object(SQNotes, "open_database", do_nothing)
        cls.open_database_patcher.start()
        
        cls.use_ascii_armor_patcher = patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
        cls.use_ascii_armor_patcher.start()
        
        cls.gpg_verified_patcher = patch.object(SQNotes,'_check_gpg_verified', do_nothing)
        cls.gpg_verified_patcher.start()
        
        cls.mock_commit_patcher = patch.object(DatabaseService, 'commit_transaction', do_nothing)
        cls.mock_commit_patcher.start()
        
        cls.check_gpg_key_email_patcher = patch.object(SQNotes, 'check_gpg_key_email', lambda x: True)
        cls.check_gpg_key_email_patcher.start()
        
        cls.mock_get_gpg_key_email_patcher = patch.object(SQNotes, 'get_gpg_key_email', lambda x :'test@test.com')
        cls.mock_get_gpg_key_email_patcher.start()
        
        cls.mock_get_notes_dir_from_config_patcher = patch.object(SQNotes, 'get_notes_dir_from_config', lambda x: 'sqnotes_notes')
        cls.mock_get_notes_dir_from_config_patcher.start()
        
        cls.mock_get_new_note_name_patcher = patch.object(SQNotes, '_get_new_note_name', lambda x: 'note1.txt')
        cls.mock_get_new_note_name_patcher.start()
        
        
    @classmethod
    def tearDownClass(cls):
        cls.open_database_patcher.stop()
        cls.use_ascii_armor_patcher.stop()
        cls.gpg_verified_patcher.stop()
        cls.mock_commit_patcher.stop()
        cls.check_gpg_key_email_patcher.stop()
        cls.mock_get_gpg_key_email_patcher.stop()
        cls.mock_get_notes_dir_from_config_patcher.stop()
        cls.mock_get_new_note_name_patcher.stop()

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        injector = Injector()
        self.sqnotes = self.sqnotes = injector.get(SQNotes)

    @patch.object(DatabaseService, 'insert_new_note_into_database', do_nothing)
    @patch.object(SQNotes, '_extract_and_save_keywords', do_nothing)
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    def test_exits_if_gpg_subprocess_exception_on_write(self, 
                                                 mock_write_encrypted_note,
                                                 ):
        """
        If encounters a GPGSubprocessException during writing
        encrypted note, application exits.
        """
        mock_write_encrypted_note.side_effect = GPGSubprocessException()
        
        test_direct_input = "a note about #apples"
        with self.assertRaises(SystemExit):
            self.sqnotes.directly_insert_note(text=test_direct_input)
            
    @patch.object(DatabaseService, 'insert_new_note_into_database', do_nothing)
    @patch.object(SQNotes, '_extract_and_save_keywords', do_nothing)
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    def test_prints_error_message_if_gpg_subprocess_exception_on_write(
                                                        self, 
                                                        mock_write_encrypted_note,
                                                            ):
        mock_write_encrypted_note.side_effect = GPGSubprocessException()
        
        test_direct_input = "a note about #apples"
        with self.assertRaises(SystemExit):
            with patch('builtins.print') as mocked_print:
                self.sqnotes.directly_insert_note(text=test_direct_input)
                printed_text = get_all_mocked_print_output(mocked_print)
                self.assertIn("error", printed_text)
                self.assertIn("GPG", printed_text)
                
        
    @patch.object(DatabaseService, 'insert_new_note_into_database', do_nothing)
    @patch.object(SQNotes, '_extract_and_save_keywords', do_nothing)
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    def test_passes_note_content_into_write_function(self, 
                                                 mock_write_encrypted_note
                                                 ):
        
        test_direct_input = "a note about #apples"
        self.sqnotes.directly_insert_note(text=test_direct_input)
        mock_write_encrypted_note.assert_called_once() 
        first_call = mock_write_encrypted_note.call_args_list[0]
        _,first_call_kwargs = first_call
        self.assertEqual(first_call_kwargs['note_content'], test_direct_input)
        
        
        
        
        
        
        
        

        