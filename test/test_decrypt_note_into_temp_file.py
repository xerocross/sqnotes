
import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes import SQNotes, TextEditorSubprocessException,\
    GPGSubprocessException
import tempfile
import sqlite3
from injector import Injector


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
        injector = Injector()
        self.sqnotes = self.sqnotes = injector.get(SQNotes)
        
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        mock_temp_file.write = lambda *args, **kwargs: None 
        self.mock_temp_file = mock_temp_file
        mock_NamedTemporaryFile = MagicMock(spec=tempfile.NamedTemporaryFile)
        
        mock_NamedTemporaryFile.return_value.__enter__.return_value = mock_temp_file
        
        self.mock_tempfile_patcher = patch('tempfile.NamedTemporaryFile', mock_NamedTemporaryFile)
        self.mock_tempfile_patcher.start()
        
    def tearDown(self):
        self.mock_tempfile_patcher.stop()
    
    @patch('subprocess.call')
    def test_calls_gpg_subprocess_with_decrypt_note_path(self, mock_subprocess):

        mock_subprocess.return_value = 0
        note_path = "test path"
        self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        mock_subprocess.assert_called_once()
        called_args, _ = mock_subprocess.call_args
        first_call = called_args[0]
        self.assertEqual(first_call[0], 'gpg')
        self.assertEqual(first_call[7], note_path)
        
        
    @patch('subprocess.call')
    def test_calls_gpg_subprocess_with_tempfile_name(self, mock_subprocess):

        mock_subprocess.return_value = 0
        note_path = "test path"
        self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        mock_subprocess.assert_called_once()
        called_args, _ = mock_subprocess.call_args
        first_call = called_args[0]
        self.assertEqual(first_call[0], 'gpg')
        self.assertEqual(first_call[5], self.mock_temp_file.name)
        
        
    @patch('subprocess.run')
    def test_decrypt_calls_raises_gpg_subprocess_exception_if_subprocess_raises_exception(self, 
                                                                                           mock_subprocess):

        mock_subprocess.side_effect = Exception()
        note_path = "test path"
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        
        
    @patch('subprocess.run')
    def test_raises_gpg_subprocess_exception_if_subprocess_returns_error_code(self, 
                                                                                           mock_subprocess):

        mock_subprocess.return_value = 1
        note_path = "test path"
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._decrypt_note_into_temp_file(note_path = note_path)
        