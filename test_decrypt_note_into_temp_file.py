
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
    
    
class TestDecryptNoteIntoTempFile(unittest.TestCase):
    # use_ascii_armor_patcher = None
    
    @classmethod
    def setUpClass(cls):
        # cls.use_ascii_armor_patcher = patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
        # cls.use_ascii_armor_patcher.start()
        pass
        
    @classmethod
    def tearDownClass(cls):
        # cls.use_ascii_armor_patcher.stop()
        pass

    
    def setUp(self):
        # self.test_dir = tempfile.TemporaryDirectory()
        self.sqnotes = SQNotes()
    
    @patch('subprocess.call')
    @patch('tempfile.NamedTemporaryFile')
    def test_decrypt_calls_gpg_subprocess_with_decrypt_note_path(self, mock_tempfile, mock_subprocess):

        mock_subprocess.return_value = 0
        
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
        
        
    @patch('subprocess.call')
    @patch('tempfile.NamedTemporaryFile')
    def test_decrypt_calls_gpg_subprocess_with_tempfile_name(self, mock_tempfile, mock_subprocess):

        mock_subprocess.return_value = 0
        
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
    def test_decrypt_calls_raises_gpg_subprocess_exception_if_subprocess_raises_exception(self, 
                                                                                           mock_tempfile, 
                                                                                           mock_subprocess):

        mock_subprocess.side_effect = Exception()
        
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        note_path = "test path"
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        
        
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    def test_decrypt_calls_raises_gpg_subprocess_exception_if_subprocess_returns_error_code(self, 
                                                                                           mock_tempfile, 
                                                                                           mock_subprocess):

        mock_subprocess.return_value = 1
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        note_path = "test path"
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        