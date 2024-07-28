
import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest

import tempfile
import sqlite3
from injector import Injector
from encrypted_note_helper import EncryptedNoteHelper, GPGSubprocessException


def get_all_mocked_print_output(mocked_print):
    call_args = mocked_print.call_args_list
    arguments_list = [args[0] for args, _ in call_args]
    all_outtext = " ".join(arguments_list)
    return all_outtext

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
    
class TestWriteEncryptedNote(unittest.TestCase):

    
    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass

    
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        injector = Injector()
        self.encrypted_note_holder = injector.get(EncryptedNoteHelper)
    
    
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
        

        config = {
            'GPG_KEY_EMAIL' : "test@test.com"
        }
        
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        self.encrypted_note_holder.write_encrypted_note(file_path, text_content, config)
        
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
        config = {
            'GPG_KEY_EMAIL' : "test@test.com"
        }
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        self.encrypted_note_holder.write_encrypted_note(file_path, text_content, config)
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
        config = {
            'GPG_KEY_EMAIL' : "test@test.com"
        }
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        with self.assertRaises(GPGSubprocessException):
            self.encrypted_note_holder.write_encrypted_note(file_path, text_content, config)
            

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
        config = {
            'GPG_KEY_EMAIL' : "test@test.com"
        }
        file_path = self.test_dir.name + os.sep + 'test.txt.gpg'
        text_content = 'test content'
        with self.assertRaises(GPGSubprocessException):
            self.encrypted_note_holder.write_encrypted_note(file_path, text_content, config)
        
