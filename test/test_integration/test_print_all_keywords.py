
import pytest
from sqnotes.sqnotes_module import SQNotes

from sqnotes.database_service import DatabaseService
from test.test_helper import get_all_mocked_print_output
from sqnotes import interface_copy


def describe_print_all_keywords():
    
    def describe_three_keywords_in_database():
        
        @pytest.mark.usefixtures("mock_open_database",
                                 "mock_transaction")
        def it_prints_all_keywords(
                                    sqnotes_obj : SQNotes,
                                    database_service : DatabaseService,
                                    mock_print
                                    ):
            cursor = database_service._get_cursor()
            new_keywords = ['apple', 'pear', 'banana']
            for k in new_keywords:
                cursor.execute('''
                        INSERT INTO keywords (keyword)
                        VALUES (?)
                    ''', (k,))
            sqnotes_obj.print_all_keywords()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            assert all(k in output for k in new_keywords)
            
    def describe_one_keyword_in_database():
        
        @pytest.mark.usefixtures("mock_open_database",
                                 "mock_transaction")
        def it_prints_the_keyword(
                                    sqnotes_obj : SQNotes,
                                    database_service : DatabaseService,
                                    mock_print
                                    ):
            cursor = database_service._get_cursor()
            new_keywords = ['orange']
            for k in new_keywords:
                cursor.execute('''
                        INSERT INTO keywords (keyword)
                        VALUES (?)
                    ''', (k,))
            sqnotes_obj.print_all_keywords()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            assert all(k in output for k in new_keywords)
            
    def describe_zero_keywords_in_database():
        
        @pytest.mark.usefixtures("mock_open_database",
                                 "mock_transaction")
        def it_prints_no_keywords_message(
                                    mock_print_to_so,
                                    sqnotes_obj : SQNotes,
                                    database_service : DatabaseService,
                                    ):
            sqnotes_obj.print_all_keywords()
            output = get_all_mocked_print_output(mocked_print=mock_print_to_so)
            expected_message = interface_copy.NO_KEYWORDS_IN_DATABASE()
            assert expected_message in output
            

