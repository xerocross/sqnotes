

from sqnotes.sqnotes_module import SQNotes

import pytest
import os
import re
import logging

from sqnotes import interface_copy
from test.test_helper import get_all_mocked_print_output_to_string,\
    get_all_mocked_print_output

logger = logging.getLogger("happy path")

def get_filename_from_confirmation_message(confirmation_message):
    note_added_message_pattern = interface_copy.NOTE_ADDED().format("([^']+)")
    match = re.search(note_added_message_pattern, confirmation_message)
    if not match:
        raise Exception("no match for filename in confirmation message")
    return match.group(1)

def describe_sqnotes_integration():

    def describe_new_note_method():
        
        
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_write_plaintext_to_temp_file",
            "mock_call_gpg_subprocess_to_write_encrypted",
            "mock_get_temp_plaintext_file"
        )
        def it_creates_a_new_note_in_notes_dir (
                            sqnotes_with_initialized_user_data : SQNotes,
                            mock_get_input_from_text_editor,
                            mock_get_new_note_name,
                            test_temp_notes_dir,
                            mock_print,
                            ):
            test_note_content = "test note content"
            mock_get_input_from_text_editor.return_value = test_note_content
            
            new_note_name = "test.txt.gpg"
            mock_get_new_note_name.side_effect = [new_note_name]
            sqnotes_with_initialized_user_data.new_note()
            output = get_all_mocked_print_output_to_string(mocked_print = mock_print)            
            created_file_name = get_filename_from_confirmation_message(output)
            created_file_path = os.path.join(test_temp_notes_dir, created_file_name)
            with open(created_file_path, 'r') as file:
                created_content = file.read()
            assert created_content == f"encrypted: {test_note_content}"
    
    
    def describe_after_directly_inserting_a_new_note():
    
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_call_gpg_subprocess_to_write_encrypted",
            "mock_decrypt_note_into_temp_file"
        )
        def it_returns_note_from_get_all_notes_method(
                                            sqnotes_with_initialized_user_data : SQNotes,
                                            mock_print
                ):
            test_note_content = "test content"
            sqnotes_with_initialized_user_data.directly_insert_note(text=test_note_content)
            output = get_all_mocked_print_output_to_string(mocked_print = mock_print)      
            created_file_name = get_filename_from_confirmation_message(output)
            all_note_paths = sqnotes_with_initialized_user_data._get_all_note_paths()
            note_names = [os.path.basename(p) for p in all_note_paths]
            assert created_file_name in note_names
    
    
    
    def describe_with_existing_note():
        
        class NoteInfo:
            
            def __init__(self, name, path, text):
                self.name = name
                self.path = path
                self.text = text
        
        
        @pytest.fixture
        def created_notes():
            created_notes = []
            yield created_notes
        
        @pytest.fixture
        def sqnotes_with_notes(
                sqnotes_with_initialized_user_data : SQNotes, 
                mock_print,
                test_temp_notes_dir,
                created_notes,
                mock_check_gpg_verified,
                mock_call_gpg_subprocess_to_write_encrypted
            ):
            
            test_note_content = "test note with #apple #pear #banana Argentina"
            sqnotes_with_initialized_user_data.directly_insert_note(text=test_note_content)
            output = get_all_mocked_print_output_to_string(mocked_print = mock_print)      
            created_file_name = get_filename_from_confirmation_message(output)
            created_file_path = os.path.join(test_temp_notes_dir, created_file_name)
            created_note_info = NoteInfo(name = created_file_name, path = created_file_path, text = test_note_content)
            created_notes.append(created_note_info)
            yield sqnotes_with_initialized_user_data
            
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_get_decrypted_content_in_memory_integration"
        )
        def it_returns_note_by_keyword(
                                        sqnotes_with_notes : SQNotes,
                                        created_notes,
                                        mock_print
                                       ):
            test_keywords = ['apple']
            sqnotes_with_notes.search_keywords(keywords=test_keywords)
            output = get_all_mocked_print_output(mocked_print=mock_print)
            noteinfo = created_notes[0]
            note_text = noteinfo.text
            assert note_text in output
            
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_get_decrypted_content_in_memory_integration"
        )
        def it_returns_note_by_text_search (
                                        sqnotes_with_notes : SQNotes,
                                        created_notes,
                                        mock_print
                                       ):
            test_search_term = ['Argentina']
            sqnotes_with_notes.search_notes(search_queries = test_search_term)
            output = get_all_mocked_print_output(mocked_print=mock_print)
            noteinfo = created_notes[0]
            note_text = noteinfo.text
            assert note_text in output
            
            
    def describe_edit_note_method():
    
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_call_gpg_subprocess_to_write_encrypted",
            "mock_decrypt_note_into_temp_file_for_integration",
            "plaintext_temp_file"
        )
        def it_writes_new_note_with_edited_content(
                                            sqnotes_with_initialized_user_data : SQNotes,
                                            test_temp_notes_dir,
                                            mock_get_edited_note_content,
                                            mock_print
                                            ):
    
            test_note_content = "test content"
            sqnotes_with_initialized_user_data.directly_insert_note(text=test_note_content)
            output = get_all_mocked_print_output_to_string(mocked_print = mock_print)      
            created_file_name = get_filename_from_confirmation_message(output)
            created_file_path = os.path.join(test_temp_notes_dir, created_file_name)
            mock_get_edited_note_content.return_value = "this has been edited"
    
            sqnotes_with_initialized_user_data.edit_note(filename=created_file_name)
            
            with open(created_file_path, 'r') as note_file:
                note_content = note_file.read()
            assert note_content == f"encrypted: this has been edited"
    
    


    

            