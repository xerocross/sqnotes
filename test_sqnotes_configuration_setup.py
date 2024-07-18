import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import pytest
from dotenv import load_dotenv
# from your_script import setup_database, add_note, extract_keywords, set_gpg_key_email, search_notes, edit_note, run_git_command
from sqnotes import SQNotes

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
class TestSQNotesConfigurationSetup(unittest.TestCase):
    
    
    def test_testing(self):
        self.assertFalse(False)