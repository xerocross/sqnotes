import unittest
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes import SQNotes, NoteNotFoundException
import tempfile

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
        
class TestSQNotesEditExistingNote(unittest.TestCase):

    def setUp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.test_dir = temp_dir
            with tempfile.NamedTemporaryFile(mode='w', dir=temp_dir, delete=False) as temp_file:
                # print(f'Temporary file created at: {temp_file.name}')
                # temp_file.write('This is some test data.')
                self.temp_file = temp_file
                self.temp_filename = os.path.basename(temp_file.name)
        self.temp_filepath = self.test_dir + os.sep + self.temp_filename
        self.sqnotes = SQNotes()
        
    
    @patch('os.path.exists')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_raises_if_note_file_not_found(self, mock_check_gpg_key, mock_get_notes_dir, mock_open_database, mock_get_gpg_key_email, mock_write_encrypted_note, mock_get_note_id, mock_delete_keywords, mock_extract_and_save_keywords, mock_get_editor, mock_os_exists):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_get_editor.return_value = 'vim'
        mock_os_exists.return_value = False
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        with pytest.raises(NoteNotFoundException):
            self.sqnotes.edit_note(filename=self.temp_filename)
        
        
    @patch('os.remove')
    @patch('os.path.exists')
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_edit_calls_to_decrypt_note(self, mock_check_gpg_key, mock_get_notes_dir, mock_open_database, mock_get_gpg_key_email, mock_write_encrypted_note, mock_get_note_id, mock_delete_keywords, mock_extract_and_save_keywords, mock_get_editor, mock_decrypt_note, mock_get_edited_note, mock_os_exists, mock_os_remove):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_get_editor.return_value = 'vim'
        mock_os_exists.return_value = True
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        
        self.sqnotes.edit_note(filename=self.temp_filename)
        mock_decrypt_note.assert_called_once()
        _, called_kwargs = mock_decrypt_note.call_args
        self.assertEqual(called_kwargs['note_path'], self.temp_filepath)
        
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    def test_descrypt_calls_gpg_subprocess_with_tempfile_name(self, mock_tempfile, mock_subprocess):
        mock_subprocess_result = Mock()
        mock_subprocess_result.returncode = 0
        mock_subprocess.return_value = mock_subprocess_result
        
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        note_path = "test path"
        self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        mock_subprocess.assert_called_once()
        called_args, _ = mock_subprocess.call_args
        first_call = called_args[0]
        self.assertEqual(first_call[0], 'gpg')
        self.assertEqual(first_call[5], mock_temp_file.name)
        
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    def test_descrypt_calls_gpg_subprocess_with_decrypt_note_path(self, mock_tempfile, mock_subprocess):
        mock_subprocess_result = Mock()
        mock_subprocess_result.returncode = 0
        mock_subprocess.return_value = mock_subprocess_result
        
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        note_path = "test path"
        self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        mock_subprocess.assert_called_once()
        called_args, _ = mock_subprocess.call_args
        first_call = called_args[0]
        self.assertEqual(first_call[0], 'gpg')
        self.assertEqual(first_call[7], note_path)
        
        
    @patch('os.remove')
    @patch('os.path.exists')
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_edit_calls_get_edited_note_with_temp_filename(self, 
                                                           mock_check_gpg_key, 
                                                           mock_get_notes_dir, 
                                                           mock_open_database, 
                                                           mock_get_gpg_key_email, 
                                                           mock_write_encrypted_note, 
                                                           mock_get_note_id, 
                                                           mock_delete_keywords, 
                                                           mock_extract_and_save_keywords, 
                                                           mock_get_editor, 
                                                           mock_decrypt_note, 
                                                           mock_get_edited_note, 
                                                           mock_os_exists, 
                                                           mock_os_remove):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_get_editor.return_value = 'vim'
        mock_os_exists.return_value = True
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        mock_decrypt_note.return_value = "temp_filename"
        
        self.sqnotes.edit_note(filename=self.temp_filename)
        mock_get_edited_note.assert_called_once()
        _, called_kwargs = mock_get_edited_note.call_args
        self.assertEqual(called_kwargs['temp_filename'], "temp_filename")
    
    
    @patch('subprocess.run')
    @patch.object(SQNotes, '_get_configured_text_editor')
    def test_get_edited_note_from_editor_opens_editor(self,
                                                      mock_get_text_editor,
                                                      mock_subprocess_run):
        mock_get_text_editor.return_value = 'vim'
        subprocess_return_mock = Mock()
        subprocess_return_mock.returncode = 0
        mock_subprocess_run.return_value = subprocess_return_mock
        temp_filename = "temp.txt"
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            note_content = self.sqnotes._get_edited_note_from_text_editor(temp_filename)
        
        mock_subprocess_run.assert_called_once()
        called_args, called_kwargs = mock_subprocess_run.call_args
        self.assertEqual(called_args[0][0], 'vim')
        

    @patch('subprocess.run')
    @patch.object(SQNotes, '_get_configured_text_editor')
    def test_get_edited_note_from_editor_opens_editor_with_tempfile_name(self,
                                                      mock_get_text_editor,
                                                      mock_subprocess_run):
        mock_get_text_editor.return_value = 'vim'
        subprocess_return_mock = Mock()
        subprocess_return_mock.returncode = 0
        mock_subprocess_run.return_value = subprocess_return_mock
        temp_filename = "temp.txt"
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            note_content = self.sqnotes._get_edited_note_from_text_editor(temp_filename)
        
        mock_subprocess_run.assert_called_once()
        called_args, called_kwargs = mock_subprocess_run.call_args
        self.assertEqual(called_args[0][1], temp_filename)

    @patch('os.remove')
    @patch('os.path.exists')
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_edit_calls_write_encrypted_note_with_path_and_content(self, 
                                                           mock_check_gpg_key, 
                                                           mock_get_notes_dir, 
                                                           mock_open_database, 
                                                           mock_get_gpg_key_email, 
                                                           mock_write_encrypted_note, 
                                                           mock_get_note_id, 
                                                           mock_delete_keywords, 
                                                           mock_extract_and_save_keywords, 
                                                           mock_get_editor, 
                                                           mock_decrypt_note, 
                                                           mock_get_edited_note, 
                                                           mock_os_exists, 
                                                           mock_os_remove):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_get_editor.return_value = 'vim'
        mock_os_exists.return_value = True
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        # mock_decrypt_note.return_value = "temp_filename"
        
        mock_get_edited_note.return_value = "note content"
        self.sqnotes.edit_note(filename=self.temp_filename)
        
        
        mock_write_encrypted_note.assert_called_once()
        _, called_kwargs = mock_write_encrypted_note.call_args
        self.assertEqual(called_kwargs['note_file_path'], self.temp_filepath)
        self.assertEqual(called_kwargs['note_content'], "note content")
