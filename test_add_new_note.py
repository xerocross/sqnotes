import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes import SQNotes, TextEditorSubprocessException,\
    GPGSubprocessException
import tempfile
import sqlite3


def get_all_mocked_print_output(mocked_print):
    call_args = mocked_print.call_args_list
    arguments_list = [args[0] for args, _ in call_args]
    all_outtext = " ".join(arguments_list)
    return all_outtext

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
        
class TestSQNotesCreateNewNote(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.sqnotes = SQNotes()

    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
        self.sqnotes.new_note()
        mock_get_input.assert_called_once()
        
    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, 'open_database', lambda x: None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_write_encrypted_note')
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

    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, 'open_database', lambda x: None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_write_encrypted_note')
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

    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
        self.sqnotes.new_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        self.assertEqual(called_kwargs['note_content'], "test content")
        
        
    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
        self.sqnotes.new_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        self.assertEqual(called_kwargs['note_file_path'], self.test_dir.name + os.sep + 'test.txt.gpg')
        
    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
            self.sqnotes.new_note()
            expected_text = f"Note added: test.txt.gpg"
            mocked_print.assert_called_once_with(expected_text)
        
    @patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_calls_subprocess_with_gpg(self, mock_subprocess_call, mock_tempfile, mock_os_exists, mock_os_remove):
        mock_subprocess_call.return_value = 0 #success
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
    
    @patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_calls_gpg_with_output_as_note_name(self, mock_subprocess_call, mock_tempfile, mock_os_exists, mock_os_remove):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_subprocess_call.return_value = 0
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
    
    @patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_raises_exception_if_gpg_subprocess_raises_exception(self, mock_subprocess_call, mock_tempfile, mock_os_exists, mock_os_remove):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_os_exists.return_value = True
        mock_subprocess_call.side_effect = Exception
        
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._write_encrypted_note(file_path, text_content)
        
    @patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_raises_exception_if_gpg_subprocess_returns_error_code(self, mock_subprocess_call, mock_tempfile, mock_os_exists, mock_os_remove):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_os_exists.return_value = True
        mock_subprocess_call.return_value = 1
        
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._write_encrypted_note(file_path, text_content)
        
    
    
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

    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, 'open_database', lambda x: None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_write_encrypted_note')
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
        
        
    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, 'open_database', lambda x: None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
    @patch.object(SQNotes, '_insert_new_note_into_database', lambda x : None)
    @patch.object(SQNotes, '_extract_and_save_keywords', lambda x : None)
    @patch.object(SQNotes, '_commit_transaction', lambda x : None)
    @patch.object(SQNotes, '_get_new_note_name')
    @patch.object(SQNotes, '_write_encrypted_note')
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
            
        
class TestSQNotesNewNoteDatabaseInteractions(unittest.TestCase):
    
    @patch.object(SQNotes, 'check_is_database_set_up', lambda x : False)
    @patch.object(SQNotes, 'get_db_file_path', lambda x,y : ':memory:')
    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda x : "")
    @patch.object(SQNotes,'set_database_is_set_up', lambda x : None)
    def setUp(self):
        self.sqnotes = SQNotes()
        self.sqnotes.open_database()
        self.connection = self.sqnotes._get_database_connection()
        self.cursor = self.sqnotes._get_database_cursor()
        
    
    def tearDown(self):

        self.connection.close()
    
    def test_insert_note_into_database_function(self):
        test_base_filename = "note_1.txt"
        note_id = self.sqnotes._insert_new_note_into_database(note_filename_base=test_base_filename)
        
        self.cursor.execute("SELECT id, filename FROM notes WHERE id = ?", (note_id,))
        result = self.cursor.fetchone()
        self.assertEqual(result[1], test_base_filename)
        self.connection.execute('ROLLBACK;')
        
        
    @patch.object(SQNotes, '_extract_keywords', lambda x,y : ['apple', 'banana'])
    def test_extract_and_save_keywords(self):
        
        test_note_content = "#apple pear #banana"
        test_base_filename = "note_1.txt"
        note_id = self.sqnotes._insert_new_note_into_database(note_filename_base=test_base_filename)
        
        self.sqnotes._extract_and_save_keywords(note_id=note_id, note_content=test_note_content)
        
        
        self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', ('apple',))
        result = self.cursor.fetchone()
        database_contains_apple_keyword = result is not None
        
        self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', ('banana',))
        result = self.cursor.fetchone()
        database_contains_banana_keyword = result is not None
        
        self.assertTrue(database_contains_apple_keyword and database_contains_banana_keyword)
        self.connection.execute('ROLLBACK;')
        
        
    def test_extract_keywords_method_gets_hashtags(self):
        test_content = "#apple pear #banana #sunrise"
        extracted_keywords = self.sqnotes._extract_keywords(content=test_content)
        self.assertCountEqual(extracted_keywords, ['apple','banana','sunrise'], 'extracted keywords did not get hashtags')
        
        
        
    def test_extract_keywords_method_does_not_produce_duples(self):
        test_content = "#apple #apple pear #banana #sunrise"
        extracted_keywords = self.sqnotes._extract_keywords(content=test_content)
        self.assertCountEqual(extracted_keywords, ['apple','banana','sunrise'], 'extracted keywords did not match hashtags')
        
        
        
        
        
        
class TestSQNotesCreateNewNoteDatabaseErrors(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.sqnotes = SQNotes()

    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
    def test_prints_cannot_open_database_message_if_error_on_open_database(self, 
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
        mock_open_database.side_effect = sqlite3.OperationalError
        
        with patch('builtins.print') as mocked_print:
            with self.assertRaises(SystemExit):
                self.sqnotes.new_note()
                print_args = mocked_print.call_args
                printed_message = print_args[0]
                self.assertIn('could not open', printed_message)

    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)        
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
    def test_exits_if_database_error_on_open_database(self, 
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
        mock_open_database.side_effect = sqlite3.OperationalError
        
        with self.assertRaises(SystemExit) as cm:
                self.sqnotes.new_note()
                self.assertEqual(cm.exception.code, 1)

        
        
    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
    def test_prints_generic_error_message_on_open_database_message_if_unknown_error_on_open_database(self, 
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
        mock_open_database.side_effect = Exception
        
        with patch('builtins.print') as mocked_print:
            with self.assertRaises(SystemExit):
                self.sqnotes.new_note()
                print_args = mocked_print.call_args
                printed_message = print_args[0]
                self.assertIn('unknown error', printed_message)


    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
    def test_exits_if_unknown_error_on_open_database(self, 
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
        mock_open_database.side_effect = Exception
        
        with self.assertRaises(SystemExit) as cm:
                self.sqnotes.new_note()
                self.assertEqual(cm.exception.code, 1)

    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
    def test_prints_database_error_message_on_error_during_database_interactions(self, 
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
        mock_insert_new_note_in_database.side_effect = sqlite3.OperationalError
        
        with patch('builtins.print') as mocked_print:
            self.sqnotes.new_note()
            call_args = mocked_print.call_args_list
            arguments_list = [args[0] for args, _ in call_args]
            all_outtext = " ".join(arguments_list)
            self.assertIn('database error', all_outtext)

        
    @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
    @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
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
    def test_prints_unexpected_error_message_on_unexpected_error_during_database_interactions(self, 
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
        mock_insert_new_note_in_database.side_effect = Exception
        
        with patch('builtins.print') as mocked_print:
            self.sqnotes.new_note()
            call_args = mocked_print.call_args_list
            arguments_list = [args[0] for args, _ in call_args]
            all_outtext = " ".join(arguments_list)
            self.assertIn('unknown error', all_outtext)
            
            
    @patch('os.remove')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_get_input_raises_exception_on_failing_subprocess_with_exception(self, mock_subprocess_call, mock_tempfile, mock_get_text_editor, mock_os_remove):
        
        mock_get_text_editor.return_value = 'vim'
        # Mock tempfile.NamedTemporaryFile context manager
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_filename = "mock_temp_file_name"
        mock_temp_file.name = mock_temp_filename
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_subprocess_call.side_effect = Exception()

        with self.assertRaises(TextEditorSubprocessException):
            self.sqnotes._get_input_from_text_editor()
        

    @patch('os.remove')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_get_input_raises_exception_on_failing_subprocess_with_nonzero_response(self, mock_subprocess_call, mock_tempfile, mock_get_text_editor, mock_os_remove):
        
        mock_get_text_editor.return_value = 'vim'
        # Mock tempfile.NamedTemporaryFile context manager
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_filename = "mock_temp_file_name"
        mock_temp_file.name = mock_temp_filename
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_subprocess_call.return_value = 1

        with self.assertRaises(TextEditorSubprocessException):
            self.sqnotes._get_input_from_text_editor()
        


