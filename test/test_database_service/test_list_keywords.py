import unittest
from unittest.mock import patch
import os
import pytest
from sqnotes.sqnotes_module import SQNotes
from dotenv import load_dotenv
from injector import Injector
from sqnotes.database_service import DatabaseService
from test.test_helper import get_all_mocked_print_output


def reload_dotenv():
    # Optionally clear existing environment variables
    for key in list(os.environ.keys()):
        if key.startswith('DATABASE_URL'):  # Adjust this as necessary for your specific environment variables
            del os.environ[key]

    # Reload the .env file
    load_dotenv(override=True)  # `override=True` ensures existing variables are overridden
    
    
def describe_list_keywords():
    
    @pytest.mark.usefixtures("mock_open_database")
    @patch.object(DatabaseService, 'get_all_keywords')
    def it_prints_all_keywords(
                                mock_get_all_keywords,
                                sqnotes_obj : SQNotes,
                                mock_print
                            ):
        keywords = ['apple', 'pear', 'banana']
        mock_get_all_keywords.return_value = keywords
        sqnotes_obj.print_all_keywords()
        output = get_all_mocked_print_output(mocked_print=mock_print)
        assert 'apple' in output
        assert 'pear' in output
        assert 'banana' in output
    

    