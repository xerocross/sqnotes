
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
    
    
class TestWriteEncryptedNote(unittest.TestCase):
    use_ascii_armor_patcher = None
    
    @classmethod
    def setUpClass(cls):
        cls.use_ascii_armor_patcher = patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
        cls.use_ascii_armor_patcher.start()
        
        
    @classmethod
    def tearDownClass(cls):
        cls.use_ascii_armor_patcher.stop()

    
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.sqnotes = SQNotes()
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_calls_gpg_with_output_as_note_name(self, 
                                                               mock_subprocess_call, 
                                                               mock_tempfile):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_subprocess_call.return_value = 0
        
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        self.sqnotes._write_encrypted_note(file_path, text_content)
        called_args, _ = mock_subprocess_call.call_args
        first_call = called_args[0]
        mock_subprocess_call.assert_called_once()
        self.assertEqual(first_call[4], '--output')
        self.assertEqual(first_call[5], file_path)
        
        
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_calls_subprocess_with_gpg(self, 
                                                      mock_subprocess_call, 
                                                      mock_tempfile):
        mock_subprocess_call.return_value = 0 #success
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        self.sqnotes._write_encrypted_note(file_path, text_content)
        called_args, called_kwargs = mock_subprocess_call.call_args
        first_call = called_args[0]
        mock_subprocess_call.assert_called_once()
        self.assertEqual(first_call[0], 'gpg')
        
        
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_raises_exception_if_gpg_subprocess_raises_exception(self, 
                                                                                mock_subprocess_call, 
                                                                                mock_tempfile):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_subprocess_call.side_effect = Exception
        
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._write_encrypted_note(file_path, text_content)
            
            

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_write_function_raises_exception_if_gpg_subprocess_returns_error_code(self, 
                                                                                  mock_subprocess_call, 
                                                                                  mock_tempfile):
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_subprocess_call.return_value = 1
        
        self.sqnotes.GPG_KEY_EMAIL = "test@test.com"
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._write_encrypted_note(file_path, text_content)
        
