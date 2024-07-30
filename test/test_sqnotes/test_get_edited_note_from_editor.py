
import unittest
from unittest.mock import patch, mock_open, Mock
import pytest
from sqnotes.sqnotes_module import SQNotes
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from injector import Injector



class TestGetEditedNoteFromEditor(unittest.TestCase):
    
    def setUp(self):
        injector = Injector()
        self.sqnotes = injector.get(SQNotes)


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
