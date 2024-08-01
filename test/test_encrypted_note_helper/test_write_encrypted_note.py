
import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest

from test.test_helper import do_nothing
import tempfile
import sqlite3
from injector import Injector
from sqnotes.encrypted_note_helper import EncryptedNoteHelper, GPGSubprocessException


@pytest.fixture
def mock_test_dir():
    test_dir = tempfile.TemporaryDirectory()
    yield test_dir

def describe_write_function():

    def describe_gpg_returns_successful():

        @pytest.mark.usefixtures('mock_NamedTemporaryFile')
        @patch('subprocess.call')
        def it_calls_gpg_with_output_as_note_name( mock_subprocess_call,
                                                    mock_encrypted_note_helper,
                                                    mock_test_dir):
            mock_subprocess_call.return_value = 0
            

            config = {
                'GPG_KEY_EMAIL' : "test@test.com"
            }
            
            file_path = mock_test_dir.name + os.sep + 'test.txt.gpg'
            text_content = 'test content'
            mock_encrypted_note_helper.write_encrypted_note(file_path, text_content, config)
            
            called_args, _ = mock_subprocess_call.call_args
            first_call = called_args[0]
            mock_subprocess_call.assert_called_once()
            assert first_call[4] == '--output'
            assert first_call[5] == file_path


        @pytest.mark.usefixtures('mock_NamedTemporaryFile')
        @patch('subprocess.call')
        def test_write_function_calls_subprocess_with_gpg(mock_subprocess_call,
                                                            mock_test_dir,
                                                            mock_encrypted_note_helper):
            mock_subprocess_call.return_value = 0 #success
            config = {
                'GPG_KEY_EMAIL' : "test@test.com"
            }
            file_path = mock_test_dir.name + os.sep + 'test.txt.gpg'
            text_content = 'test content'
            mock_encrypted_note_helper.write_encrypted_note(file_path, text_content, config)
            called_args, called_kwargs = mock_subprocess_call.call_args
            first_call = called_args[0]
            mock_subprocess_call.assert_called_once()
            assert first_call[0] == 'gpg'

    def describe_gpg_raises_exception():
        @pytest.mark.usefixtures('mock_NamedTemporaryFile')
        @patch('subprocess.call')
        def it_raises_exception(mock_subprocess_call,
                                mock_test_dir,
                                mock_encrypted_note_helper):
            
            mock_subprocess_call.side_effect = Exception
            config = {
                'GPG_KEY_EMAIL' : "test@test.com"
            }
            file_path = mock_test_dir.name + os.sep + 'test.txt.gpg'
            text_content = 'test content'
            with pytest.raises(GPGSubprocessException):
                mock_encrypted_note_helper.write_encrypted_note(file_path, text_content, config)

    def describe_gpg_returns_error_code():
        @pytest.mark.usefixtures('mock_NamedTemporaryFile')
        @patch('subprocess.call')
        def ir_raises_exception( mock_subprocess_call,
                                mock_test_dir,
                                mock_encrypted_note_helper):
            
            mock_subprocess_call.return_value = 1
            config = {
                'GPG_KEY_EMAIL' : "test@test.com"
            }
            file_path = mock_test_dir.name + os.sep + 'test.txt.gpg'
            text_content = 'test content'
            with pytest.raises(GPGSubprocessException):
                mock_encrypted_note_helper.write_encrypted_note(file_path, text_content, config)
        
