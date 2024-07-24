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

    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_calls_to_get_input_from_text_editor(self, 
                                                 mock_check_gpg_key, 
                                                 mock_get_notes_dir, 
                                                 mock_open_database, 
                                                 mock_get_input, 
                                                 mock_get_gpg_key_email, 
                                                 mock_write_encrypted_note, 
                                                 mock_insert_new_note_in_database, 
                                                 mock_extract_keywords, 
                                                 mock_get_new_note_name,
                                                 mock_commit_transaction):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir.name
        mock_get_input.return_value = "test content"
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_write_encrypted_note.return_value = True
        self.sqnotes.add_note()
        mock_get_input.assert_called_once()
        
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_passes_content_from_editor_into_write_function(self, 
                                                            mock_check_gpg_key, 
                                                            mock_get_notes_dir, 
                                                            mock_open_database, 
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
        self.sqnotes.add_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        self.assertEqual(called_kwargs['note_content'], "test content")
        
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_passes_new_note_name_into_write_function(self, 
                                                      mock_check_gpg_key, 
                                                      mock_get_notes_dir, 
                                                      mock_open_database, 
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
        self.sqnotes.add_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        self.assertEqual(called_kwargs['note_file_path'], self.test_dir.name + os.sep + 'test.txt.gpg')
        

    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, '_get_input_from_text_editor')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_prints_message_saying_note_was_created(self, 
                                                    mock_check_gpg_key, 
                                                    mock_get_notes_dir, 
                                                    mock_open_database, 
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
            self.sqnotes.add_note()
            expected_text = f"Note added: test.txt.gpg"
            mocked_print.assert_called_once_with(expected_text)
        
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_calls_subprocess_with_gpg(self, mock_subprocess_call, mock_tempfile, mock_os_exists, mock_os_remove):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_os_exists.return_value = True
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        self.sqnotes._write_encrypted_note(file_path, text_content)
        called_args, called_kwargs = mock_subprocess_call.call_args
        first_call = called_args[0]
        mock_subprocess_call.assert_called_once()
        self.assertEqual(first_call[0], 'gpg')
    
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_calls_gpg_with_output_as_note_name(self, mock_subprocess_call, mock_tempfile, mock_os_exists, mock_os_remove):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        
        mock_os_exists.return_value = True
        
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        self.sqnotes._write_encrypted_note(file_path, text_content)
        called_args, _ = mock_subprocess_call.call_args
        first_call = called_args[0]
        mock_subprocess_call.assert_called_once()
        self.assertEqual(first_call[4], '--output')
        self.assertEqual(first_call[5], file_path)
    
    @patch('os.remove')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_input_function_gets_text_editor_from_config(self, mock_subprocess_call, mock_tempfile, mock_get_text_editor, mock_os_remove):
        
        mock_get_text_editor.return_value = 'vim'
        # Mock tempfile.NamedTemporaryFile context manager
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file

        # Mock subprocess.call to simulate editing
        mock_subprocess_call.return_value = 0  # Simulate successful call

        # Mock open to return mock content
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            self.sqnotes._get_input_from_text_editor()

        mock_subprocess_call.assert_called_once()
        called_args, _ = mock_subprocess_call.call_args
        first_called_args = called_args[0]
        self.assertEqual(first_called_args[0], 'vim')

        
    @patch('os.remove')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_input_function_calls_subprocess_with_correct_temp_filename(self, mock_subprocess_call, mock_tempfile, mock_get_text_editor, mock_os_remove):
        
        mock_get_text_editor.return_value = 'vim'
        # Mock tempfile.NamedTemporaryFile context manager
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_filename = "mock_temp_file_name"
        mock_temp_file.name = mock_temp_filename
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file

        # Mock subprocess.call to simulate editing
        mock_subprocess_call.return_value = 0  # Simulate successful call

        # Mock open to return mock content
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            note_content = self.sqnotes._get_input_from_text_editor()

        mock_subprocess_call.assert_called_once()
        called_args, _ = mock_subprocess_call.call_args
        first_called_args = called_args[0]
        self.assertEqual(first_called_args[1], mock_temp_filename)

    
    @patch('os.remove')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_input_function_returns_content_from_text_editor(self, mock_subprocess_call, mock_tempfile, mock_get_text_editor, mock_os_remove):
        
        # Mock tempfile.NamedTemporaryFile context manager
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file

        # Mock subprocess.call to simulate editing
        mock_subprocess_call.return_value = 0  # Simulate successful call

        # Mock open to return mock content
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            note_content = self.sqnotes._get_input_from_text_editor()

        # Assert the returned note_content is as expected
        self.assertEqual(note_content, 'Mock note content')

        
        
        
        
        
        
        
        
        
