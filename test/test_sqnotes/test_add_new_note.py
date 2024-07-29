import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes.sqnotes_module import SQNotes, TextEditorSubprocessException,\
    GPGSubprocessException
import tempfile
import sqlite3
from injector import Injector
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
import injector


def get_all_mocked_print_output(mocked_print):
    call_args = mocked_print.call_args_list
    arguments_list = [args[0] for args, _ in call_args]
    all_outtext = " ".join(arguments_list)
    return all_outtext

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
        
class TestSQNotesCreateNewNote(unittest.TestCase):
    open_database_patcher = None
    use_ascii_armor_patcher = None
    get_configured_text_editor_patcher = None
    gpg_verified_patcher = None

    @classmethod
    def setUpClass(cls):
        cls.open_database_patcher = patch.object(SQNotes, "open_database", lambda x: None)
        cls.open_database_patcher.start()
        
        cls.use_ascii_armor_patcher = patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
        cls.use_ascii_armor_patcher.start()
        
        cls.get_configured_text_editor_patcher = patch.object(SQNotes,  '_get_configured_text_editor', lambda x: 'vim')
        cls.get_configured_text_editor_patcher.start()
        
        cls.gpg_verified_patcher = patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
        cls.gpg_verified_patcher.start()
        
        
        
    @classmethod
    def tearDownClass(cls):
        cls.open_database_patcher.stop()
        cls.use_ascii_armor_patcher.stop()
        cls.get_configured_text_editor_patcher.stop()
        cls.gpg_verified_patcher.stop()

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        injector = Injector()
        self.sqnotes = injector.get(SQNotes)


    
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    def test_calls_to_get_input_from_text_editor(self,
                                                 mock_write_encrypted_note,
                                                 mock_check_gpg_key, 
                                                 mock_get_notes_dir, 
                                                 mock_get_input, 
                                                 mock_get_gpg_key_email, 
                                                 mock_insert_new_note_in_database, 
                                                 mock_extract_keywords, 
                                                 mock_get_new_note_name,
                                                 mock_commit_transaction):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_write_encrypted_note.return_value = True
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        self.sqnotes.new_note()
        mock_get_input.assert_called_once()
        
    
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_on_text_editor_subprocess_exception_prints_proper_message(self, 
                                                 mock_check_gpg_key, 
                                                 mock_get_notes_dir, 
                                                 mock_get_input, 
                                                 mock_get_gpg_key_email, 
                                                 mock_write_encrypted_note, 
                                                 mock_get_new_note_name):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.side_effect = TextEditorSubprocessException()
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        
        with self.assertRaises(SystemExit):
            with patch('builtins.print') as mocked_print:
                self.sqnotes.new_note()
                printed_text = get_all_mocked_print_output(mocked_print)
                self.assertIn("Encountered an error attempting to open the configured text editor", printed_text)

    
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_on_text_editor_subprocess_exception_exits(self, 
                                                 mock_check_gpg_key, 
                                                 mock_get_notes_dir, 
                                                 mock_get_input, 
                                                 mock_get_gpg_key_email, 
                                                 mock_write_encrypted_note, 
                                                 mock_get_new_note_name):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.side_effect = TextEditorSubprocessException()
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        
        with self.assertRaises(SystemExit) as ex:
            self.sqnotes.new_note()
            self.assertEqual(ex.exception.code, 1)

    
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_passes_content_from_editor_into_write_function(self, 
                                                            mock_check_gpg_key, 
                                                            mock_get_notes_dir, 
                                                            mock_get_input, 
                                                            mock_get_gpg_key_email, 
                                                            mock_write_encrypted_note, 
                                                            mock_insert_new_note_in_database, 
                                                            mock_extract_keywords, 
                                                            mock_get_new_note_name,
                                                            mock_commit_transaction
                                                            ):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        self.sqnotes.new_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        self.assertEqual(called_kwargs['note_content'], "test content")
        
        
    
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_passes_new_note_name_into_write_function(self, 
                                                      mock_check_gpg_key, 
                                                      mock_get_notes_dir, 
                                                      mock_get_input, 
                                                      mock_get_gpg_key_email, 
                                                      mock_write_encrypted_note, 
                                                      mock_insert_new_note_in_database, 
                                                      mock_extract_keywords, 
                                                      mock_get_new_note_name,
                                                      mock_commit_transaction):
        mock_get_new_note_name.return_value = 'test.txt.gpg'
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        self.sqnotes.new_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        self.assertEqual(called_kwargs['note_file_path'], self.test_dir.name + os.sep + 'test.txt.gpg')
        
    
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_prints_message_saying_note_was_created(self, 
                                                    mock_check_gpg_key, 
                                                    mock_get_notes_dir, 
                                                    mock_get_input, 
                                                    mock_get_gpg_key_email, 
                                                    mock_write_encrypted_note, 
                                                    mock_insert_new_note_in_database, 
                                                    mock_extract_keywords, 
                                                    mock_get_new_note_name,
                                                    mock_commit_transaction
                                                    ):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        with patch('builtins.print') as mocked_print:
            self.sqnotes.new_note()
            expected_text = f"Note added: test.txt.gpg"
            mocked_print.assert_called_once_with(expected_text)
        
    
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, 'open_database', lambda x: None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_exits_on_gpg_subprocess_exception_during_write(self, 
                                                 mock_check_gpg_key, 
                                                 mock_get_notes_dir, 
                                                 mock_get_input, 
                                                 mock_get_gpg_key_email, 
                                                 mock_write_encrypted_note, 
                                                 mock_get_new_note_name):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_get_input.return_value = "test input"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        mock_write_encrypted_note.side_effect = GPGSubprocessException()
        
        with self.assertRaises(SystemExit) as ex:
            self.sqnotes.new_note()
            self.assertEqual(ex.exception.code, 1)
        
        
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, 'open_database', lambda x: None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    @patch('builtins.print')
    def test_prints_error_message_on_gpg_subprocess_exception_during_write(self, 
                                                 mock_print_function,
                                                 mock_check_gpg_key, 
                                                 mock_get_notes_dir, 
                                                 mock_get_input, 
                                                 mock_get_gpg_key_email, 
                                                 mock_write_encrypted_note, 
                                                 mock_get_new_note_name):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_get_input.return_value = "test input"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        mock_write_encrypted_note.side_effect = GPGSubprocessException()
        
        with self.assertRaises(SystemExit):
            self.sqnotes.new_note()
            output = get_all_mocked_print_output(mocked_print=mock_print_function)
            self.assertIn('Encountered an error while attempting to call GPG', output)
            
        

    
        

    
        


