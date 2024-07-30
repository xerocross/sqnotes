
import unittest
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes.sqnotes_module import SQNotes, NoteNotFoundException,\
     GPGSubprocessException,\
    TextEditorSubprocessException
import tempfile
from test.test_sqnotes.test_add_new_note import get_all_mocked_print_output
from injector import Injector

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
    
def delete_temp_file(*args, **kwargs):
    pass
        
class TestGetInputFromTextEditor(unittest.TestCase):
    delete_temp_file_patcher = None
    
    @classmethod
    def setUpClass(cls):
        cls.delete_temp_file_patcher = patch.object(SQNotes, "_delete_temp_file", delete_temp_file)
        cls.delete_temp_file_patcher.start()

        
    @classmethod
    def tearDownClass(cls):
        cls.delete_temp_file_patcher.stop()



    def setUp(self):
        injector = Injector()
        self.sqnotes = injector.get(SQNotes)
        self.TEXT_EDITOR = 'vim'
        mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_temp_file.name = "mock_temp_file_name"
        self.mock_temp_file = mock_temp_file
        
        mock_tempfile = MagicMock(spec=tempfile.NamedTemporaryFile)
        mock_tempfile.return_value.__enter__.return_value = self.mock_temp_file
        
        self.mock_tempfile_patcher = patch('tempfile.NamedTemporaryFile', mock_tempfile)
        self.mock_tempfile_patcher.start()
        self.mock_note_content = 'Mock content'
        mock_open_function = mock_open(read_data=self.mock_note_content)
        
        self.mock_open_patcher = patch('builtins.open', mock_open_function)
        self.mock_open_patcher.start()
        
        
        
    def tearDown(self):
        self.mock_tempfile_patcher.stop()
        self.mock_open_patcher.stop()
        

    @patch('subprocess.call')
    def test_input_function_calls_subprocess_with_correct_temp_filename(self, 
                                                                        mock_subprocess_call):
        

        # Mock subprocess.call to simulate editing
        mock_subprocess_call.return_value = 0  # Simulate successful call

        self.sqnotes._get_input_from_text_editor(TEXT_EDITOR=self.TEXT_EDITOR)

        mock_subprocess_call.assert_called_once()
        called_args, _ = mock_subprocess_call.call_args
        first_called_args = called_args[0]
        self.assertEqual(first_called_args[1], self.mock_temp_file.name)

        
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_returns_content_from_text_editor(self, 
                                              mock_subprocess_call, 
                                              mock_tempfile):
        

        # Mock subprocess.call to simulate editing
        mock_subprocess_call.return_value = 0  # Simulate successful call
        note_content = self.sqnotes._get_input_from_text_editor(TEXT_EDITOR=self.TEXT_EDITOR)

        self.assertEqual(note_content, self.mock_note_content)    
    
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_get_input_raises_exception_on_failing_subprocess_with_exception(self, 
                                                                             mock_subprocess_call, 
                                                                             mock_tempfile):
        

        mock_subprocess_call.side_effect = Exception()

        with self.assertRaises(TextEditorSubprocessException):
            self.sqnotes._get_input_from_text_editor(TEXT_EDITOR = self.TEXT_EDITOR)
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_get_input_raises_exception_on_failing_subprocess_with_nonzero_response(self, 
                                                                                    mock_subprocess_call, 
                                                                                    mock_tempfile):

        mock_subprocess_call.return_value = 1
        with self.assertRaises(TextEditorSubprocessException):
            self.sqnotes._get_input_from_text_editor(TEXT_EDITOR=self.TEXT_EDITOR)
    
        
        