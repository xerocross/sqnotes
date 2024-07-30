
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes.database_service import DatabaseService
from test.test_helper import do_nothing

def describe_extract_and_save_keywords():
    
    @patch.object(DatabaseService, 'insert_note_keyword_into_database', do_nothing)
    @patch.object(DatabaseService, 'insert_keyword_into_database')
    @patch.object(SQNotes, '_extract_keywords')
    def it_calls_to_insert_each_new_keyword(mock_extract_keywords,
                                        mock_insert_keyword_into_database,
                                        sqnotes_obj : SQNotes):
        note_id = 11
        note_content = 'test #apple #pear banana'
        mock_extract_keywords.return_value = ['apple', 'pear']
        sqnotes_obj._extract_and_save_keywords(note_id, note_content)
        call_args_list = mock_insert_keyword_into_database.call_args_list
        assert call_args_list[0].kwargs['keyword'] == 'apple'
        assert call_args_list[1].kwargs['keyword'] == 'pear'
        