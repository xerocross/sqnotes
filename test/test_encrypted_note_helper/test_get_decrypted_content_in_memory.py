
import os
import pytest
import unittest
from unittest.mock import patch, Mock
from injector import Injector
from encrypted_note_helper import EncryptedNoteHelper, GPGSubprocessException, CouldNotReadNoteException


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    


@pytest.fixture
def encrypted_note_helper():
    intector = Injector()
    enh = intector.get(EncryptedNoteHelper)
    yield enh


@pytest.fixture
def mock_open_function():
    mock_open_function = unittest.mock.mock_open(read_data='Mock note content')
    with patch('builtins.open', mock_open_function):
        yield mock_open_function


@patch('subprocess.run')
def test_raises_gpg_subprocess_exception_if_gpg_returns_error_code(mock_subprocess,
                                                                   mock_open_function,
                                                                   encrypted_note_helper):
    process = Mock()
    process.returncode = 2
    mock_subprocess.return_value = process
    note_path = "testpath.txt"
    with pytest.raises(GPGSubprocessException):
        encrypted_note_helper.get_decrypted_content_in_memory(note_path=note_path)
    
    
@patch('subprocess.run')
def test_raises_gpg_subprocess_exception_if_gpg_raises_exception(mock_subprocess,
                                                                   mock_open_function,
                                                                   encrypted_note_helper):
    mock_subprocess.side_effect = Exception()
    note_path = "testpath.txt"
    with pytest.raises(GPGSubprocessException):
        encrypted_note_helper.get_decrypted_content_in_memory(note_path=note_path)
        
        
@patch('subprocess.run')
def test_raises_read_error_if_opening_note_file_raises_exception(mock_subprocess,
                                                                   mock_open_function,
                                                                   encrypted_note_helper):
    process = Mock()
    process.returncode = 0
    mock_subprocess.return_value = process
    note_path = "testpath.txt"
    mock_open_function.side_effect = Exception()
    with pytest.raises(CouldNotReadNoteException):
        encrypted_note_helper.get_decrypted_content_in_memory(note_path=note_path)
        
        
        