
import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes import SQNotes, TextEditorSubprocessException,\
    GPGSubprocessException
import tempfile
import sqlite3
from test.test_helper import get_all_mocked_print_output

def side_effect_callable():
    side_effect_callable.called = getattr(side_effect_callable, "called", 0) + 1
    if side_effect_callable.called == 1:
        raise ValueError("Simulated exception")
    else:
        return 0


def configure_text_editor(*args, **kwargs):
    pass

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
    
class TestChooseTextEditorInteractive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        pass
        
    @classmethod
    def tearDownClass(cls):
        pass

    
    def setUp(self):
        self.sqnotes = SQNotes()

        
    def tearDown(self):
        pass
        
    @patch.object(SQNotes, '_get_available_text_editors', lambda x : ['vim', 'nano'])
    @patch.object(SQNotes, '_configure_text_editor', configure_text_editor)
    @patch('builtins.input', lambda x: '0')
    @patch('builtins.print')
    def test_prints_list_of_available_editors_if_multiple(self, 
                                                          mock_print):
        self.sqnotes.choose_text_editor_interactive()
        output = get_all_mocked_print_output(mocked_print=mock_print)
        self.assertIn('Please choose a text editor', output)
        self.assertIn('vim', output)
        self.assertIn('nano', output)
        
        
    @patch.object(SQNotes, '_get_available_text_editors', lambda x : ['vim', 'nano'])
    @patch.object(SQNotes, '_configure_text_editor', configure_text_editor)
    @patch('builtins.input')
    @patch('builtins.print')
    def test_prompts_user_select_index(self, 
                                       mock_print,
                                       mock_input):
        self.sqnotes.choose_text_editor_interactive()
        output = get_all_mocked_print_output(mocked_print=mock_print)
        mock_input.assert_called_once()
        
        
    @patch.object(SQNotes, '_get_available_text_editors', lambda x : ['vim', 'nano'])
    @patch.object(SQNotes, '_configure_text_editor')
    @patch('builtins.int', lambda x : 0)
    @patch('builtins.input')
    @patch('builtins.print')
    def test_sets_editor_if_user_selection_input_valid_vim(self, 
                                       mock_print,
                                       mock_input,
                                       mock_configure_text_editor):
        self.sqnotes.choose_text_editor_interactive()
        mock_input.side_effect = ['0']
        mock_configure_text_editor.assert_called_once_with(editor = 'vim')
        
    @patch.object(SQNotes, '_get_available_text_editors', lambda x : ['vim', 'nano'])
    @patch('builtins.int', lambda x : 1)
    @patch.object(SQNotes, '_configure_text_editor')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_sets_editor_if_user_selection_input_valid_nano(self, 
                                       mock_print,
                                       mock_input,
                                       mock_configure_text_editor):
        self.sqnotes.choose_text_editor_interactive()
        output = get_all_mocked_print_output(mocked_print=mock_print)
        mock_input.side_effect = ['1']
        mock_configure_text_editor.assert_called_once_with(editor = 'nano')
    #
    # @patch.object(SQNotes, '_get_available_text_editors', lambda x : ['vim', 'nano'])
    # @patch('builtins.int')
    # @patch.object(SQNotes, '_configure_text_editor')
    # @patch('builtins.input')
    # @patch('builtins.print')
    # def test_repeats_prompt_if_input_not_a_number(self, 
    #                                    mock_print,
    #                                    mock_input,
    #                                    mock_configure_text_editor,
    #                                    mock_int):
    #     self.sqnotes.choose_text_editor_interactive()
    #     mock_input.side_effect = ['apple', '1']
    #     mock_int.side_effect = side_effect_callable
    #     mock_input_calls = mock_input.call_args_list
    #     self.assertEqual(len(mock_input_calls), 2)
        
        
        
        
        
        
    