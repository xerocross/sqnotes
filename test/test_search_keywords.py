

from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes import SQNotes, GPGSubprocessException
from test.test_helper import get_all_mocked_print_output
import logging
from test.test_sqnotes_initializer import get_test_sqnotes


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_notes_by_keyword (*args, **kwargs):
    return ['note1.txt', 'note2.txt']

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
@pytest.fixture
def sqnotes_obj():
    sqnotes_obj = get_test_sqnotes()
    yield sqnotes_obj
    
    
@patch.object(SQNotes, 'get_notes_dir_from_config', lambda x: "notes_dir")
@patch.object(SQNotes, '_query_notes_by_keywords', get_notes_by_keyword)
@patch.object(SQNotes, 'open_database', lambda x : None)
@patch('builtins.print')
@patch.object(SQNotes, '_get_decrypted_content_in_memory')
def test_exits_if_get_decrypted_content_raises_gpg_exception(
                                                                        mock_get_decrypted_content,
                                                                        mock_print,
                                                                        sqnotes_obj
                                                                    ):
    mock_get_decrypted_content.side_effect = GPGSubprocessException()
    with pytest.raises(SystemExit):
        sqnotes_obj.search_keywords(keywords=["apple"])
    
    

@patch.object(SQNotes, 'get_notes_dir_from_config', lambda x: "notes_dir")
@patch.object(SQNotes, '_query_notes_by_keywords', get_notes_by_keyword)
@patch.object(SQNotes, 'open_database', lambda x : None)
@patch('builtins.print')
@patch.object(SQNotes, '_get_decrypted_content_in_memory')
def test_prints_error_message_if_get_decrypted_content_raises_gpg_exception(
                                                                        mock_get_decrypted_content,
                                                                        mock_print,
                                                                        sqnotes_obj
                                                                    ):
    mock_get_decrypted_content.side_effect = GPGSubprocessException()
    with pytest.raises(SystemExit):
        sqnotes_obj.search_keywords(keywords=["apple"])
    output = get_all_mocked_print_output(mocked_print=mock_print)
    print("output:")
    print(output)
    logger.debug(f"output: {output}")
    logger.debug(mock_print)
    assert "Encountered an error while attempting to call GPG." in output
    assert "Exiting" in output
    
    
    
    
    
    
    