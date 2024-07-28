
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes import SQNotes, GPGSubprocessException
from test.test_helper import get_all_mocked_print_output, get_all_single_arg_inputs
import logging
from injector import Injector


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_notes_by_keyword (*args, **kwargs):
    return ['note1.txt', 'note2.txt']

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
@pytest.fixture
def sqnotes_obj():
    injector = Injector()
    sqnotes_obj = injector.get(SQNotes)
    sqnotes_obj.DEFAULT_NOTE_DIR = "test_dir"
    yield sqnotes_obj
    
@patch('builtins.input')
def test_prompts_user_for_path_input(mock_input,
                                     sqnotes_obj):
    sqnotes_obj.prompt_for_user_notes_path()
    mock_input.assert_called()
    inputs = get_all_single_arg_inputs(mocked_fn=mock_input)
    assert any('enter a path' in input for input in inputs)
    
@patch.object(SQNotes, '_try_to_make_path')
@patch('builtins.input')
def test_returns_path_if_make_path_successful(
                                    mock_input,
                                    mock_make_path,
                                    sqnotes_obj
                                    ):
    mock_make_path.return_value = True
    test_path = "mypath"
    mock_input.return_value = test_path
    submitted_path = sqnotes_obj.prompt_for_user_notes_path()
    assert submitted_path == test_path
    
    
@patch.object(SQNotes, '_try_to_make_path')
@patch('builtins.input')
def test_prompt_repeats_if_user_input_unsuccessful_successful_second_try(
                                    mock_input,
                                    mock_make_path,
                                    sqnotes_obj):
    mock_make_path.side_effect = [False, True]
    test_path = "mypath"
    mock_input.return_value = test_path
    sqnotes_obj.prompt_for_user_notes_path()
    call_args_list = mock_input.call_args_list
    assert len(call_args_list) == 2
    


@patch('builtins.print')
@patch.object(SQNotes, '_try_to_make_path')
@patch('builtins.input')
def test_prints_try_again_message_on_unsuccessful_first_attempt(
                                    mock_input,
                                    mock_make_path,
                                    mock_print,
                                    sqnotes_obj):
    mock_make_path.side_effect = [False, True]
    test_path = "mypath"
    mock_input.return_value = test_path
    sqnotes_obj.prompt_for_user_notes_path()
    output = get_all_mocked_print_output(mocked_print=mock_print)
    assert "try again" in output
    
    
    
    