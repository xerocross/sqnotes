
import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes
from sqnotes.database_service import DatabaseService

def describe_sqnote_module():

    def describe_extract_and_save_keywords():
        
        def it_inserts_hashtags_in_database(
                                            sqnotes_obj : SQNotes,
                                            database_service_open_in_memory : DatabaseService
                                            ):
            test_note_content = "#apple pear #banana"
            test_base_filename = "note_1.txt"
            note_id = database_service_open_in_memory.insert_new_note_into_database(note_filename_base = test_base_filename)
            sqnotes_obj._extract_and_save_keywords(note_id=note_id, note_content=test_note_content)
            cursor = database_service_open_in_memory._get_cursor()
            cursor.execute('SELECT id FROM keywords WHERE keyword = ?', ('apple',))
            result = cursor.fetchone()
            database_contains_apple_keyword = result is not None
            assert database_contains_apple_keyword
            cursor.execute('SELECT id FROM keywords WHERE keyword = ?', ('banana',))
            result = cursor.fetchone()
            database_contains_banana_keyword = result is not None
            assert database_contains_banana_keyword
            cursor.execute('ROLLBACK;')
            
            

