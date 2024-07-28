

from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes import SQNotes, GPGSubprocessException
from test.test_helper import get_all_mocked_print_output
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_notes_by_keyword (*args, **kwargs):
    return ['note1.txt', 'note2.txt']

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
@pytest.fixture
def sqnotes_obj():
    sqnotes_obj = SQNotes()
    
    yield sqnotes_obj
    
    
    