

import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes.database_service import DatabaseService

def describe_print_all_keywords():
    
    @pytest.mark.usefixtures("mock_open_database")
    @patch.object(DatabaseService, 'get_all_keywords')
    def it_calls_database_service_to_get_keywords(
                                            mock_get_all_keywords,
                                            mock_print,
                                            sqnotes_obj : SQNotes
            ):
        mock_get_all_keywords.return_value = []
        sqnotes_obj.print_all_keywords()
        mock_get_all_keywords.assert_called_once()