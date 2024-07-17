import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
# import tempfile
# from datetime import datetime
# import sqlite3
# import subprocess
# import configparser
# import re
import pytest
from dotenv import load_dotenv
# from your_script import setup_database, add_note, extract_keywords, set_gpg_key_email, search_notes, edit_note, run_git_command
from sqnotes import SQNotes



@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'

class TestSQNotes(unittest.TestCase):

    
    def setUp(self):
        self.sqnotes = SQNotes()

    def test_testCase(self):
        assert True
        

    # @patch('subprocess.call')
    # def test_run_git_command_passes_through(self, mock_subprocess_call):
    #     self.sqnotes.run_git_command(['status'])
    #     default_notes_path = os.getenv('DEFAULT_NOTES_PATH')
    #     mock_subprocess_call.assert_called_once_with(['git', 'status'], cwd=os.path.expanduser(default_notes_path))

    # @patch('subprocess.call')
    # def test_add_note_creates_temp_file(self, mock_subprocess_call):
    #     with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp_file:
    #         set_gpg_key_email("test@example.com")
    #         add_note()
    #         mock_temp_file.assert_called()
    #         mock_subprocess_call.assert_called()

    # @patch('subprocess.call')
    # def test_set_gpg_key_email(self, mock_subprocess_call):
    #     set_gpg_key_email("test@example.com")
    #     self.assertEqual(GPG_KEY_EMAIL, "test@example.com")
    #
    # def test_extract_keywords(self):
    #     content = "This is a test note with #keywords and #morekeywords."
    #     expected_keywords = ['keywords', 'morekeywords']
    #     self.assertEqual(extract_keywords(content), expected_keywords)
    #

    # Add more tests here as needed


class TestConfigurationSetup(unittest.TestCase):
    pass
    # @patch('os.mkdir')
    # def test_creates_config_if_not_exists(self):
    #     config_dir = os.getenv('DEFAULT_CONFIG_DIR_PATH')
    #     pass
    #


class TestTryToMakePath(unittest.TestCase):
    
    def setUp(self):
        self.sqnotes = SQNotes()
    
    
    def test_returns_true_on_path_exists(self):
        selected_path = 'test_path'
        with patch('os.path.exists', return_value=True): 
            response = self.sqnotes.try_to_make_path(selected_path)
            self.assertTrue(response, "received false, which indicates failure")


class TestDatabaseInteractions(unittest.TestCase):
    pass
    # def create_database_tables_does_not_raise_error(self):
    #     pass


if __name__ == '__main__':
    unittest.main()
