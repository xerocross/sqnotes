

import pytest
from unittest import TestCase
from unittest.mock import patch


from sqnotes.database_service import DatabaseService,\
    NoteNotFoundInDatabaseException


def describe_database_service():
    
    def describe_insert_note_into_database():

        def it_puts_note_in_database(
                                    database_service_open_in_memory : DatabaseService
                                    ):
            test_base_filename = "note_1.txt"
            note_id = database_service_open_in_memory.insert_new_note_into_database(note_filename_base=test_base_filename)
            connection = database_service_open_in_memory._get_connection()
            cursor = database_service_open_in_memory._get_cursor()
            
            cursor.execute("SELECT id, filename FROM notes WHERE id = ?", (note_id,))
            result = cursor.fetchone()
            assert result[1] == test_base_filename
            connection.execute('ROLLBACK;')

         
      



    # def test_deletes_keywords_from_note_before_adding_new_keywords(self):
    #     test_filename = "note_1.txt"
    #     note_id = 5
    #     keyword_id = 1
    #     self.cursor.execute("INSERT INTO keywords (id, keyword) VALUES (?, ?)", (keyword_id, 'apple'))
    #     self.cursor.execute("INSERT INTO notes (id, filename) VALUES (?, ?)", (note_id, test_filename))
    #     self.cursor.execute("INSERT INTO note_keywords (note_id, keyword_id) VALUES (?, ?)", (note_id, keyword_id))
    #     self.cursor.execute("SELECT * from note_keywords WHERE note_id = ?", (note_id,))
    #     rows = self.cursor.fetchall()
    #     a_keyword_existed_before_delete = len(rows) == 1
    #
    #     self.sqnotes._delete_keywords_from_database_for_note(note_id)
    #
    #     self.cursor.execute("SELECT * from note_keywords WHERE note_id = ?", (note_id,))
    #
    #     rows = self.cursor.fetchall()
    #     no_keywords_existed_after_delete = len(rows) == 0
    #     self.assertTrue(a_keyword_existed_before_delete and no_keywords_existed_after_delete)
    #     self.connection.execute('ROLLBACK;')


#
#
# class TestSQNotesNewNoteDatabaseInteractions(unittest.TestCase):
#
#     @patch.object(SQNotes, '_check_is_database_set_up', lambda x : False)
#     @patch.object(SQNotes, 'get_db_file_path', lambda x,y : ':memory:')
#     @patch.object(SQNotes, 'get_notes_dir_from_config', lambda x : "")
#     @patch.object(SQNotes,'_set_database_is_set_up', lambda x : None)
#     def setUp(self):
#         injector = Injector()
#         self.py = self.py = injector.get(SQNotes)
#         self.py.open_database()
#         self.connection = self.py._get_database_connection()
#         self.cursor = self.py._get_database_cursor()
#
#
#     def tearDown(self):
#
#         self.connection.close()
#
#     def test_insert_note_into_database_function(self):
#         test_base_filename = "note_1.txt"
#         note_id = self.py._insert_new_note_into_database(note_filename_base=test_base_filename)
#
#         self.cursor.execute("SELECT id, filename FROM notes WHERE id = ?", (note_id,))
#         result = self.cursor.fetchone()
#         self.assertEqual(result[1], test_base_filename)
#         self.connection.execute('ROLLBACK;')
#
#
#     @patch.object(SQNotes, '_extract_keywords', lambda x,y : ['apple', 'banana'])
#     def test_extract_and_save_keywords(self):
#
#         test_note_content = "#apple pear #banana"
#         test_base_filename = "note_1.txt"
#         note_id = self.py._insert_new_note_into_database(note_filename_base=test_base_filename)
#
#         self.py._extract_and_save_keywords(note_id=note_id, note_content=test_note_content)
#
#
#         self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', ('apple',))
#         result = self.cursor.fetchone()
#         database_contains_apple_keyword = result is not None
#
#         self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', ('banana',))
#         result = self.cursor.fetchone()
#         database_contains_banana_keyword = result is not None
#
#         self.assertTrue(database_contains_apple_keyword and database_contains_banana_keyword)
#         self.connection.execute('ROLLBACK;')
#
#
#     def test_extract_keywords_method_gets_hashtags(self):
#         test_content = "#apple pear #banana #sunrise"
#         extracted_keywords = self.py._extract_keywords(content=test_content)
#         self.assertCountEqual(extracted_keywords, ['apple','banana','sunrise'], 'extracted keywords did not get hashtags')
#
#
#
#     def test_extract_keywords_method_does_not_produce_duples(self):
#         test_content = "#apple #apple pear #banana #sunrise"
#         extracted_keywords = self.py._extract_keywords(content=test_content)
#         self.assertCountEqual(extracted_keywords, ['apple','banana','sunrise'], 'extracted keywords did not match hashtags')
#
#
#
#
#
#
# class TestSQNotesCreateNewNoteDatabaseErrors(unittest.TestCase):
#     gpg_verified_patcher = None
#     get_configured_text_editor_patcher = None
#     use_ascii_armor_patcher = None
#
#     @classmethod
#     def setUpClass(cls):
#         cls.gpg_verified_patcher = patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
#         cls.gpg_verified_patcher.start()
#
#         cls.get_configured_text_editor_patcher = patch.object(SQNotes,  '_get_configured_text_editor', lambda x: 'vim')
#         cls.get_configured_text_editor_patcher.start()
#
#         cls.use_ascii_armor_patcher = patch.object(SQNotes, '_is_use_ascii_armor', lambda _ : False)
#         cls.use_ascii_armor_patcher.start()
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.gpg_verified_patcher.stop()
#         cls.get_configured_text_editor_patcher.stop()
#         cls.use_ascii_armor_patcher.stop()
#
#     def setUp(self):
#         self.test_dir = tempfile.TemporaryDirectory()
#         injector = Injector()
#         self.py = self.py = injector.get(SQNotes)
#
#     @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
#     @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
#     @patch.object(SQNotes, '_commit_transaction')
#     @patch.object(SQNotes, '_get_new_note_name')
#     @patch.object(SQNotes, '_extract_and_save_keywords')
#     @patch.object(SQNotes, '_insert_new_note_into_database')
#     @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
#     @patch.object(SQNotes, 'get_gpg_key_email')
#     @patch.object(SQNotes, '_get_input_from_text_editor')
#     @patch.object(SQNotes, 'open_database')
#     @patch.object(SQNotes, 'get_notes_dir_from_config')
#     @patch.object(SQNotes, 'check_gpg_key_email')
#     def test_prints_cannot_open_database_message_if_error_on_open_database(self, 
#                                                  mock_check_gpg_key, 
#                                                  mock_get_notes_dir, 
#                                                  mock_open_database, 
#                                                  mock_get_input, 
#                                                  mock_get_gpg_key_email, 
#                                                  mock_write_encrypted_note, 
#                                                  mock_insert_new_note_in_database, 
#                                                  mock_extract_keywords, 
#                                                  mock_get_new_note_name,
#                                                  mock_commit_transaction):
#         mock_get_new_note_name.return_value = "test.txt.gpg"
#         mock_check_gpg_key.return_value = True
#         mock_get_notes_dir.return_value = self.test_dir.name
#         mock_get_input.return_value = "test content"
#         mock_get_gpg_key_email.return_value = "test@test.com"
#         mock_write_encrypted_note.return_value = True
#         mock_open_database.side_effect = sqlite3.OperationalError
#
#         with patch('builtins.print') as mocked_print:
#             with self.assertRaises(SystemExit):
#                 self.py.new_note()
#                 print_args = mocked_print.call_args
#                 printed_message = print_args[0]
#                 self.assertIn('could not open', printed_message)
#
#     @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)        
#     @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
#     @patch.object(SQNotes, '_commit_transaction')
#     @patch.object(SQNotes, '_get_new_note_name')
#     @patch.object(SQNotes, '_extract_and_save_keywords')
#     @patch.object(SQNotes, '_insert_new_note_into_database')
#     @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
#     @patch.object(SQNotes, 'get_gpg_key_email')
#     @patch.object(SQNotes, '_get_input_from_text_editor')
#     @patch.object(SQNotes, 'open_database')
#     @patch.object(SQNotes, 'get_notes_dir_from_config')
#     @patch.object(SQNotes, 'check_gpg_key_email')
#     def test_exits_if_database_error_on_open_database(self, 
#                                                  mock_check_gpg_key, 
#                                                  mock_get_notes_dir, 
#                                                  mock_open_database, 
#                                                  mock_get_input, 
#                                                  mock_get_gpg_key_email, 
#                                                  mock_write_encrypted_note, 
#                                                  mock_insert_new_note_in_database, 
#                                                  mock_extract_keywords, 
#                                                  mock_get_new_note_name,
#                                                  mock_commit_transaction):
#         mock_get_new_note_name.return_value = "test.txt.gpg"
#         mock_check_gpg_key.return_value = True
#         mock_get_notes_dir.return_value = self.test_dir.name
#         mock_get_input.return_value = "test content"
#         mock_get_gpg_key_email.return_value = "test@test.com"
#         mock_write_encrypted_note.return_value = True
#         mock_open_database.side_effect = sqlite3.OperationalError
#
#         with self.assertRaises(SystemExit) as cm:
#                 self.py.new_note()
#                 self.assertEqual(cm.exception.code, 1)
#
#
#
#     @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
#     @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
#     @patch.object(SQNotes, '_commit_transaction')
#     @patch.object(SQNotes, '_get_new_note_name')
#     @patch.object(SQNotes, '_extract_and_save_keywords')
#     @patch.object(SQNotes, '_insert_new_note_into_database')
#     @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
#     @patch.object(SQNotes, 'get_gpg_key_email')
#     @patch.object(SQNotes, '_get_input_from_text_editor')
#     @patch.object(SQNotes, 'open_database')
#     @patch.object(SQNotes, 'get_notes_dir_from_config')
#     @patch.object(SQNotes, 'check_gpg_key_email')
#     def test_prints_generic_error_message_on_open_database_message_if_unknown_error_on_open_database(self, 
#                                                  mock_check_gpg_key, 
#                                                  mock_get_notes_dir, 
#                                                  mock_open_database, 
#                                                  mock_get_input, 
#                                                  mock_get_gpg_key_email, 
#                                                  mock_write_encrypted_note, 
#                                                  mock_insert_new_note_in_database, 
#                                                  mock_extract_keywords, 
#                                                  mock_get_new_note_name,
#                                                  mock_commit_transaction):
#         mock_get_new_note_name.return_value = "test.txt.gpg"
#         mock_check_gpg_key.return_value = True
#         mock_get_notes_dir.return_value = self.test_dir.name
#         mock_get_input.return_value = "test content"
#         mock_get_gpg_key_email.return_value = "test@test.com"
#         mock_write_encrypted_note.return_value = True
#         mock_open_database.side_effect = Exception
#
#         with patch('builtins.print') as mocked_print:
#             with self.assertRaises(SystemExit):
#                 self.py.new_note()
#                 print_args = mocked_print.call_args
#                 printed_message = print_args[0]
#                 self.assertIn('unknown error', printed_message)
#
#
#     @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
#     @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
#     @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
#     @patch.object(SQNotes, '_commit_transaction')
#     @patch.object(SQNotes, '_get_new_note_name')
#     @patch.object(SQNotes, '_extract_and_save_keywords')
#     @patch.object(SQNotes, '_insert_new_note_into_database')
#     @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
#     @patch.object(SQNotes, 'get_gpg_key_email')
#     @patch.object(SQNotes, '_get_input_from_text_editor')
#     @patch.object(SQNotes, 'open_database')
#     @patch.object(SQNotes, 'get_notes_dir_from_config')
#     @patch.object(SQNotes, 'check_gpg_key_email')
#     def test_exits_if_unknown_error_on_open_database(self, 
#                                                  mock_check_gpg_key, 
#                                                  mock_get_notes_dir, 
#                                                  mock_open_database, 
#                                                  mock_get_input, 
#                                                  mock_get_gpg_key_email, 
#                                                  mock_write_encrypted_note, 
#                                                  mock_insert_new_note_in_database, 
#                                                  mock_extract_keywords, 
#                                                  mock_get_new_note_name,
#                                                  mock_commit_transaction):
#         mock_get_new_note_name.return_value = "test.txt.gpg"
#         mock_check_gpg_key.return_value = True
#         mock_get_notes_dir.return_value = self.test_dir.name
#         mock_get_input.return_value = "test content"
#         mock_get_gpg_key_email.return_value = "test@test.com"
#         mock_write_encrypted_note.return_value = True
#         mock_open_database.side_effect = Exception
#
#         with self.assertRaises(SystemExit) as cm:
#                 self.py.new_note()
#                 self.assertEqual(cm.exception.code, 1)
#
#     @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
#     @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
#     @patch.object(SQNotes, '_commit_transaction')
#     @patch.object(SQNotes, '_get_new_note_name')
#     @patch.object(SQNotes, '_extract_and_save_keywords')
#     @patch.object(SQNotes, '_insert_new_note_into_database')
#     @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
#     @patch.object(SQNotes, 'get_gpg_key_email')
#     @patch.object(SQNotes, '_get_input_from_text_editor')
#     @patch.object(SQNotes, 'open_database')
#     @patch.object(SQNotes, 'get_notes_dir_from_config')
#     @patch.object(SQNotes, 'check_gpg_key_email')
#     def test_prints_database_error_message_on_error_during_database_interactions(self, 
#                                                  mock_check_gpg_key, 
#                                                  mock_get_notes_dir, 
#                                                  mock_open_database, 
#                                                  mock_get_input, 
#                                                  mock_get_gpg_key_email, 
#                                                  mock_write_encrypted_note, 
#                                                  mock_insert_new_note_in_database, 
#                                                  mock_extract_keywords, 
#                                                  mock_get_new_note_name,
#                                                  mock_commit_transaction):
#         mock_get_new_note_name.return_value = "test.txt.gpg"
#         mock_check_gpg_key.return_value = True
#         mock_get_notes_dir.return_value = self.test_dir.name
#         mock_get_input.return_value = "test content"
#         mock_get_gpg_key_email.return_value = "test@test.com"
#         mock_write_encrypted_note.return_value = True
#         mock_insert_new_note_in_database.side_effect = sqlite3.OperationalError
#
#         with patch('builtins.print') as mocked_print:
#             self.py.new_note()
#             call_args = mocked_print.call_args_list
#             arguments_list = [args[0] for args, _ in call_args]
#             all_outtext = " ".join(arguments_list)
#             self.assertIn('database error', all_outtext)
#
#
#     @patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
#     @patch.object(SQNotes, 'check_text_editor_is_configured', lambda _ : None)
#     @patch.object(SQNotes, '_commit_transaction')
#     @patch.object(SQNotes, '_get_new_note_name')
#     @patch.object(SQNotes, '_extract_and_save_keywords')
#     @patch.object(SQNotes, '_insert_new_note_into_database')
#     @patch.object(EncryptedNoteHelper, 'write_encrypted_note')
#     @patch.object(SQNotes, 'get_gpg_key_email')
#     @patch.object(SQNotes, '_get_input_from_text_editor')
#     @patch.object(SQNotes, 'open_database')
#     @patch.object(SQNotes, 'get_notes_dir_from_config')
#     @patch.object(SQNotes, 'check_gpg_key_email')
#     def test_prints_unexpected_error_message_on_unexpected_error_during_database_interactions(self, 
#                                                  mock_check_gpg_key, 
#                                                  mock_get_notes_dir, 
#                                                  mock_open_database, 
#                                                  mock_get_input, 
#                                                  mock_get_gpg_key_email, 
#                                                  mock_write_encrypted_note, 
#                                                  mock_insert_new_note_in_database, 
#                                                  mock_extract_keywords, 
#                                                  mock_get_new_note_name,
#                                                  mock_commit_transaction):
#         mock_get_new_note_name.return_value = "test.txt.gpg"
#         mock_check_gpg_key.return_value = True
#         mock_get_notes_dir.return_value = self.test_dir.name
#         mock_get_input.return_value = "test content"
#         mock_get_gpg_key_email.return_value = "test@test.com"
#         mock_write_encrypted_note.return_value = True
#         mock_insert_new_note_in_database.side_effect = Exception
#
#         with patch('builtins.print') as mocked_print:
#             self.py.new_note()
#             call_args = mocked_print.call_args_list
#             arguments_list = [args[0] for args, _ in call_args]
#             all_outtext = " ".join(arguments_list)
#             self.assertIn('unknown error', all_outtext)
#



def describe_get_note_id_or_raise():

    def describe_if_note_exists():
        
        def it_returns_correct_note_id(
                                    database_service_open_in_memory : DatabaseService
                                    ):
            
            """
                If note is in the database, calling to get the note id from the
                filename correctly finds the note and gets the id.
            """
            test_filename = "note_1.txt"
            cursor = database_service_open_in_memory._get_cursor()
            cursor.execute("INSERT INTO notes (filename) VALUES (?)", (test_filename,))
            test_note_id = cursor.lastrowid
    
            received_note_id = database_service_open_in_memory.get_note_id_from_database_or_raise(filename=test_filename)
            assert received_note_id == test_note_id, "did not get correct id from database"
            cursor.execute('ROLLBACK;')
            
            
    def describe_if_note_does_not_exist():
        
        def it_raises_note_not_found_exception (
                    database_service_open_in_memory : DatabaseService
                    ):
            test_filename = "note_1.txt"
            with pytest.raises(NoteNotFoundInDatabaseException):
                database_service_open_in_memory.get_note_id_from_database_or_raise(filename=test_filename)
            
