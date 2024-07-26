import unittest
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes import SQNotes, NoteNotFoundException,\
    NoteNotFoundInDatabaseException, GPGSubprocessException
import tempfile
from test_add_new_note import get_all_mocked_print_output

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
        
class TestSQNotesEditExistingNote(unittest.TestCase):
    open_database_patcher = None
    get_configured_text_editor_patcher = None
    gpg_verified_patcher = None
    gpg_email_key_patcher = None
    
    @classmethod
    def setUpClass(cls):
        cls.open_database_patcher = patch.object(SQNotes, "open_database", lambda x: None)
        cls.open_database_patcher.start()
        
        cls.get_configured_text_editor_patcher = patch.object(SQNotes,  '_get_configured_text_editor', lambda x: 'vim')
        cls.get_configured_text_editor_patcher.start()
        
        cls.gpg_verified_patcher = patch.object(SQNotes,'_check_gpg_verified', lambda x : None)
        cls.gpg_verified_patcher.start()
        
        cls.gpg_email_key_patcher = patch.object(SQNotes, 'get_gpg_key_email', lambda x : 'test@test.com')
        cls.gpg_email_key_patcher.start()
        
    @classmethod
    def tearDownClass(cls):
        cls.open_database_patcher.stop()
        cls.get_configured_text_editor_patcher.stop()
        cls.gpg_verified_patcher.stop()
        cls.gpg_email_key_patcher.stop()

    def setUp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.test_dir = temp_dir
            with tempfile.NamedTemporaryFile(mode='w', dir=temp_dir, delete=False) as temp_file:
                # print(f'Temporary file created at: {temp_file.name}')
                # temp_file.write('This is some test data.')
                self.temp_file = temp_file
                self.temp_filename = os.path.basename(temp_file.name)
        self.temp_filepath = self.test_dir + os.sep + self.temp_filename
        self.sqnotes = SQNotes()
        
    
    @patch('os.path.exists')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_raise')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_raises_if_note_file_not_found(self, 
                                           mock_check_gpg_key, 
                                           mock_get_notes_dir, 
                                           mock_open_database, 
                                           mock_write_encrypted_note, 
                                           mock_get_note_id, 
                                           mock_delete_keywords, 
                                           mock_extract_and_save_keywords, 
                                           mock_get_editor, 
                                           mock_os_exists):
        mock_get_editor.return_value = 'vim'
        mock_os_exists.return_value = False
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        with pytest.raises(NoteNotFoundException):
            self.sqnotes.edit_note(filename=self.temp_filename)
        
        
    @patch('os.remove', lambda x: None)
    @patch('os.path.exists', lambda x: True)
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, '_commit_transaction', lambda x: None)
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_raise')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_edit_calls_to_decrypt_note(self, 
                                        mock_check_gpg_key, 
                                        mock_get_notes_dir, 
                                        mock_open_database, 
                                        mock_get_gpg_key_email, 
                                        mock_write_encrypted_note, 
                                        mock_get_note_id, 
                                        mock_delete_keywords, 
                                        mock_extract_and_save_keywords,
                                        mock_decrypt_note, 
                                        mock_get_edited_note):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        
        self.sqnotes.edit_note(filename=self.temp_filename)
        mock_decrypt_note.assert_called_once()
        _, called_kwargs = mock_decrypt_note.call_args
        self.assertEqual(called_kwargs['note_path'], self.temp_filepath)
        
    @patch('os.remove', lambda x: None)
    @patch('os.path.exists', lambda x: True)
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, '_commit_transaction', lambda x: None)
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_raise')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_exits_if_decryption_raises_gpg_subprocess_exception(self, 
                                        mock_check_gpg_key, 
                                        mock_get_notes_dir, 
                                        mock_open_database, 
                                        mock_get_gpg_key_email, 
                                        mock_write_encrypted_note, 
                                        mock_get_note_id, 
                                        mock_delete_keywords, 
                                        mock_extract_and_save_keywords,
                                        mock_decrypt_note, 
                                        mock_get_edited_note):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        mock_decrypt_note.side_effect = GPGSubprocessException()
    
        with self.assertRaises(SystemExit) as ex:
            self.sqnotes.edit_note(filename=self.temp_filename)
        self.assertEqual(ex.exception.code, 1)

        
    @patch('os.remove', lambda x: None)
    @patch('os.path.exists', lambda x: True)
    @patch('builtins.print')
    @patch.object(SQNotes, '_get_configured_text_editor', lambda x: 'vim')
    @patch.object(SQNotes, '_commit_transaction', lambda x: None)
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_raise')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_prints_gpg_error_if_decryption_raises_gpg_subprocess_exception(self, 
                                        mock_check_gpg_key, 
                                        mock_get_notes_dir, 
                                        mock_open_database, 
                                        mock_get_gpg_key_email, 
                                        mock_write_encrypted_note, 
                                        mock_get_note_id, 
                                        mock_delete_keywords, 
                                        mock_extract_and_save_keywords,
                                        mock_decrypt_note, 
                                        mock_get_edited_note,
                                        mock_print):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        mock_decrypt_note.side_effect = GPGSubprocessException()
        
        with self.assertRaises(SystemExit):
            self.sqnotes.edit_note(filename=self.temp_filename)
        output = get_all_mocked_print_output(mocked_print=mock_print)
        self.assertIn('Encountered an error while attempting to call GPG.', output)
            
        

    @patch('os.remove')
    @patch('os.path.exists')
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_raise')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_edit_calls_get_edited_note_with_temp_filename(self, 
                                                           mock_check_gpg_key, 
                                                           mock_get_notes_dir, 
                                                           mock_open_database, 
                                                           mock_get_gpg_key_email, 
                                                           mock_write_encrypted_note, 
                                                           mock_get_note_id, 
                                                           mock_delete_keywords, 
                                                           mock_extract_and_save_keywords, 
                                                           mock_get_editor, 
                                                           mock_decrypt_note, 
                                                           mock_get_edited_note,
                                                           mock_commit_transaction, 
                                                           mock_os_exists, 
                                                           mock_os_remove):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_get_editor.return_value = 'vim'
        mock_os_exists.return_value = True
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        mock_decrypt_note.return_value = "temp_filename"
        
        self.sqnotes.edit_note(filename=self.temp_filename)
        mock_get_edited_note.assert_called_once()
        _, called_kwargs = mock_get_edited_note.call_args
        self.assertEqual(called_kwargs['temp_filename'], "temp_filename")
    
    
    @patch('subprocess.run')
    @patch.object(SQNotes, '_get_configured_text_editor')
    def test_get_edited_note_from_editor_opens_editor(self,
                                                      mock_get_text_editor,
                                                      mock_subprocess_run):
        mock_get_text_editor.return_value = 'vim'
        subprocess_return_mock = Mock()
        subprocess_return_mock.returncode = 0
        mock_subprocess_run.return_value = subprocess_return_mock
        temp_filename = "temp.txt"
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            note_content = self.sqnotes._get_edited_note_from_text_editor(temp_filename)
        
        mock_subprocess_run.assert_called_once()
        called_args, called_kwargs = mock_subprocess_run.call_args
        self.assertEqual(called_args[0][0], 'vim')
        

    @patch('subprocess.run')
    @patch.object(SQNotes, '_get_configured_text_editor')
    def test_get_edited_note_from_editor_opens_editor_with_tempfile_name(self,
                                                      mock_get_text_editor,
                                                      mock_subprocess_run):
        mock_get_text_editor.return_value = 'vim'
        subprocess_return_mock = Mock()
        subprocess_return_mock.returncode = 0
        mock_subprocess_run.return_value = subprocess_return_mock
        temp_filename = "temp.txt"
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            note_content = self.sqnotes._get_edited_note_from_text_editor(temp_filename)
        
        mock_subprocess_run.assert_called_once()
        called_args, called_kwargs = mock_subprocess_run.call_args
        self.assertEqual(called_args[0][1], temp_filename)

    @patch('os.remove')
    @patch('os.path.exists')
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_get_edited_note_from_text_editor')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    @patch.object(SQNotes, '_get_configured_text_editor')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_raise')
    @patch.object(SQNotes, '_write_encrypted_note')
    @patch.object(SQNotes, 'get_gpg_key_email')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, 'check_gpg_key_email')
    def test_edit_calls_write_encrypted_note_with_path_and_content(self, 
                                                           mock_check_gpg_key, 
                                                           mock_get_notes_dir, 
                                                           mock_open_database, 
                                                           mock_get_gpg_key_email, 
                                                           mock_write_encrypted_note, 
                                                           mock_get_note_id, 
                                                           mock_delete_keywords, 
                                                           mock_extract_and_save_keywords, 
                                                           mock_get_editor, 
                                                           mock_decrypt_note, 
                                                           mock_get_edited_note,
                                                           mock_commit_transaction, 
                                                           mock_os_exists, 
                                                           mock_os_remove):
        mock_get_gpg_key_email.return_value = "test@test.com"
        mock_get_editor.return_value = 'vim'
        mock_os_exists.return_value = True
        mock_check_gpg_key.return_value = True
        mock_get_notes_dir.return_value = self.test_dir
        # mock_decrypt_note.return_value = "temp_filename"
        
        mock_get_edited_note.return_value = "note content"
        self.sqnotes.edit_note(filename=self.temp_filename)
        
        
        mock_write_encrypted_note.assert_called_once()
        _, called_kwargs = mock_write_encrypted_note.call_args
        self.assertEqual(called_kwargs['note_file_path'], self.temp_filepath)
        self.assertEqual(called_kwargs['note_content'], "note content")



class TestSQNotesEditNoteDatabaseInteractions(unittest.TestCase):
    
    @patch.object(SQNotes, '_check_is_database_set_up', lambda x : False)
    @patch.object(SQNotes, 'get_db_file_path', lambda x,y : ':memory:')
    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda x : "")
    @patch.object(SQNotes,'_set_database_is_set_up', lambda x : None)
    def setUp(self):
        self.sqnotes = SQNotes()
        self.sqnotes.open_database()
        self.connection = self.sqnotes._get_database_connection()
        self.cursor = self.sqnotes._get_database_cursor()
        
        
        
    def test_get_note_id_from_database_gets_id_if_note_exists(self):
        """
            If note is in the database, calling to get the note id from the
            filename correctly finds the note and gets the id.
        """
        test_filename = "note_1.txt"
        self.cursor.execute("INSERT INTO notes (filename) VALUES (?)", (test_filename,))
        test_note_id = self.cursor.lastrowid
        
        received_note_id = self.sqnotes._get_note_id_from_database_or_raise(filename=test_filename)
        self.assertEqual(received_note_id, test_note_id, "did not get correct id from database")
        self.connection.execute('ROLLBACK;')
        
        
    def test_get_note_id_from_database__or_raise_raises_if_note_does_not_exist(self):
        """
            If note is not in the database, calling to get the note id from the
            filename raises NoteNotFoundInDatabaseException
        """

        test_filename = "note_1.txt"
        with self.assertRaises(NoteNotFoundInDatabaseException):
            self.sqnotes._get_note_id_from_database_or_raise(filename=test_filename)

    def test_deletes_keywords_from_note_before_adding_new_keywords(self):
        test_filename = "note_1.txt"
        note_id = 5
        keyword_id = 1
        self.cursor.execute("INSERT INTO keywords (id, keyword) VALUES (?, ?)", (keyword_id, 'apple'))
        self.cursor.execute("INSERT INTO notes (id, filename) VALUES (?, ?)", (note_id, test_filename))
        self.cursor.execute("INSERT INTO note_keywords (note_id, keyword_id) VALUES (?, ?)", (note_id, keyword_id))
        self.cursor.execute("SELECT * from note_keywords WHERE note_id = ?", (note_id,))
        rows = self.cursor.fetchall()
        a_keyword_existed_before_delete = len(rows) == 1
        
        self.sqnotes._delete_keywords_from_database_for_note(note_id)
        
        self.cursor.execute("SELECT * from note_keywords WHERE note_id = ?", (note_id,))
        
        rows = self.cursor.fetchall()
        no_keywords_existed_after_delete = len(rows) == 0
        self.assertTrue(a_keyword_existed_before_delete and no_keywords_existed_after_delete)
        self.connection.execute('ROLLBACK;')











