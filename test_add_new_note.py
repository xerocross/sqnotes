import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes import SQNotes
import tempfile

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
        
class TestSQNotesCreateNewNote(unittest.TestCase):

    
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.sqnotes = SQNotes()

    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_calls_to_get_input_from_text_editor(self, mock_check_gpg_key, mock_get_notes_dir, mock_open_database, mock_get_input, mock_get_gpg_key_email, mock_write_encrypted_note, mock_insert_new_note_in_database, mock_extract_keywords, mock_get_new_note_name):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        self.sqnotes.add_note()
        mock_get_input.assert_called_once()
        
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_passes_content_from_editor_into_write_function(self, mock_check_gpg_key, mock_get_notes_dir, mock_open_database, mock_get_input, mock_get_gpg_key_email, mock_write_encrypted_note, mock_insert_new_note_in_database, mock_extract_keywords, mock_get_new_note_name):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        self.sqnotes.add_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        self.assertEqual(called_kwargs['note_content'], "test content")

    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_prints_message_saying_note_was_created(self, mock_check_gpg_key, mock_get_notes_dir, mock_open_database, mock_get_input, mock_get_gpg_key_email, mock_write_encrypted_note, mock_insert_new_note_in_database, mock_extract_keywords, mock_get_new_note_name):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        with patch('builtins.print') as mocked_print:
            self.sqnotes.add_note()
            expected_text = f"Note added: test.txt.gpg"
            mocked_print.assert_called_once_with(expected_text)
        
    
