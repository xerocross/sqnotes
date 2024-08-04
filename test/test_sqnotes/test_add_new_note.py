import os
import sqlite3
from unittest.mock import patch

import pytest

from sqnotes import interface_copy
from sqnotes.database_service import DatabaseService
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from sqnotes.sqnotes_module import (
    SQNotes,
    TextEditorSubprocessException,
    GPGSubprocessException,
)
from test.test_helper import (
    do_nothing,
    just_return,
    get_all_mocked_print_output,
    get_all_mocked_print_output_to_string,
)


def describe_the_new_note_method():

    def describe_error_on_open_database():

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_write_encrypted_note",
            "mock_insert_new_note_into_database",
            "mock_get_configured_text_editor",
            "mock_get_notes_dir_from_config",
            "mock_get_input_from_text_editor",
            "mock_get_is_initialized"
        )
        def it_exits(sqnotes_obj, mock_open_database):
            mock_open_database.side_effect = sqlite3.OperationalError
            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_write_encrypted_note",
            "mock_insert_new_note_into_database",
            "mock_get_configured_text_editor",
            "mock_get_notes_dir_from_config",
            "mock_get_input_from_text_editor",
            "mock_get_is_initialized"
        )
        def it_prints_database_error_message(
            mock_open_database, mock_get_input_from_text_editor, mock_print, sqnotes_obj
        ):

            mock_open_database.side_effect = sqlite3.OperationalError
            mock_get_input_from_text_editor.return_value = "test content"
            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()
                output = get_all_mocked_print_output(mocked_print=mock_print)
                expected_error_message = interface_copy.COULD_NOT_OPEN_DATABASE()
                assert expected_error_message in output

    @pytest.mark.usefixtures(
        "mock_check_gpg_key_email",
        "mock_is_use_ascii_armor",
        "mock_get_configured_text_editor",
        "mock_check_gpg_verified",
        "mock_check_text_editor_is_configured",
        "mock_commit_transaction",
        "mock_extract_and_save_keywords",
        "mock_open_database",
        "mock_get_new_note_name",
        "mock_get_gpg_key_email",
        "mock_write_encrypted_note",
        "mock_insert_new_note_into_database",
        "mock_get_configured_text_editor",
        "mock_get_notes_dir_from_config",
        "mock_get_input_from_text_editor",
            "mock_get_is_initialized"
    )
    @patch.object(EncryptedNoteHelper, "write_encrypted_note")
    def it_calls_to_get_input_from_text_editor(
        mock_write_encrypted_note,
        mock_get_input_from_text_editor,
        sqnotes_obj,
    ):
        mock_write_encrypted_note.return_value = True
        mock_get_input_from_text_editor.return_value = "test content"
        sqnotes_obj.new_note()
        mock_get_input_from_text_editor.assert_called_once()

    def describe_text_editor_subprocess_exception():

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_write_encrypted_note",
            "mock_insert_new_note_into_database",
            "mock_get_configured_text_editor",
            "mock_get_notes_dir_from_config",
            "mock_get_input_from_text_editor",
            "mock_get_is_initialized"
        )
        def it_prints_proper_error_message(
                                                sqnotes_obj,
                                                mock_get_input_from_text_editor,
                                                mock_print
                                            ):
            mock_get_input_from_text_editor.side_effect = TextEditorSubprocessException()
            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()
                printed_text = get_all_mocked_print_output(mocked_print=mock_print)
                expected_message = (
                    interface_copy.TEXT_EDITOR_SUBPROCESS_ERROR().format("vim")
                )
                assert expected_message in printed_text

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_open_database",
            "mock_write_encrypted_note",
            "mock_insert_new_note_into_database",
            "mock_get_configured_text_editor",
            "mock_get_is_initialized"
        )
        @patch.object(SQNotes, "_get_input_from_text_editor")
        @patch.object(SQNotes, "get_notes_dir_from_config")
        def it_exits(
            mock_get_notes_dir,
            mock_get_input_from_text_editor,
            test_configuration_dir,
            sqnotes_obj,
        ):
            mock_get_notes_dir.return_value = test_configuration_dir
            mock_get_input_from_text_editor.side_effect = (
                TextEditorSubprocessException()
            )

            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()

    def describe_database_error_during_database_insert_note():

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_open_database",
            "mock_write_encrypted_note",
            "mock_get_is_initialized"
        )
        @patch.object(SQNotes, "_check_for_database_exception", just_return(True))
        @patch.object(SQNotes, "_get_input_from_text_editor")
        @patch.object(SQNotes, "get_notes_dir_from_config")
        def it_prints_database_error_message(
            mock_get_notes_dir,
            mock_get_input,
            mock_insert_new_note_into_database,
            test_configuration_dir,
            sqnotes_obj,
            mock_print,
        ):
            mock_get_notes_dir.return_value = test_configuration_dir
            mock_get_input.return_value = "test content"
            mock_insert_new_note_into_database.side_effect = Exception

            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()
                output = get_all_mocked_print_output(mocked_print=mock_print)
                expected_error_message = interface_copy.DATABASE_EXCEPTION_MESSAGE()
                data_not_saved = interface_copy.DATA_NOT_SAVED()
                assert expected_error_message in output
                assert data_not_saved in output

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_open_database",
            "mock_write_encrypted_note",
            "mock_get_is_initialized"
        )
        @patch.object(SQNotes, "_check_for_database_exception", just_return(True))
        @patch.object(SQNotes, "_get_input_from_text_editor")
        @patch.object(SQNotes, "get_notes_dir_from_config")
        def it_exits(
            mock_get_notes_dir,
            mock_get_input,
            mock_insert_new_note_into_database,
            test_configuration_dir,
            sqnotes_obj,
        ):
            mock_get_notes_dir.return_value = test_configuration_dir
            mock_get_input.return_value = "test content"
            mock_insert_new_note_into_database.side_effect = Exception

            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()

    def describe_unexpected_error_during_database_insert_note():

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_open_database",
            "mock_write_encrypted_note",
            "mock_get_is_initialized"
        )
        @patch.object(DatabaseService, "insert_new_note_into_database")
        @patch.object(SQNotes, "_get_input_from_text_editor")
        @patch.object(SQNotes, "get_notes_dir_from_config")
        def it_exits(
            mock_get_notes_dir,
            mock_get_input,
            mock_insert_new_note_in_database,
            test_configuration_dir,
            sqnotes_obj,
        ):
            mock_get_notes_dir.return_value = test_configuration_dir
            mock_get_input.return_value = "test content"
            mock_insert_new_note_in_database.side_effect = Exception

            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_open_database",
            "mock_get_new_note_name",
            "mock_write_encrypted_note",
            "mock_get_gpg_key_email",
            "mock_get_notes_dir_from_config",
            "mock_get_is_initialized"
        )
        @patch.object(SQNotes, "_get_input_from_text_editor")
        def test_prints_unexpected_error_message(
            mock_get_input,
            mock_insert_new_note_into_database,
            sqnotes_obj,
        ):
            
            mock_get_input.return_value = "test content"
            mock_insert_new_note_into_database.side_effect = Exception
            with pytest.raises(SystemExit):
                with patch("builtins.print") as mocked_print:
                    sqnotes_obj.new_note()
                    output = get_all_mocked_print_output(mocked_print=mocked_print)
                    expected_error_message = interface_copy.UNKNOWN_ERROR()
                    assert expected_error_message in output

    @pytest.mark.usefixtures(
        "mock_check_gpg_verified",
        "mock_get_configured_text_editor",
        "mock_open_database",
        "mock_is_use_ascii_armor",
        "mock_check_gpg_key_email",
        "mock_extract_and_save_keywords",
        "mock_insert_new_note_into_database",
        "mock_check_text_editor_is_configured",
        "mock_commit_transaction",
        "mock_get_notes_dir_from_config",
        "mock_get_gpg_key_email",
            "mock_get_is_initialized"
    )
    @patch.object(SQNotes, "_get_input_from_text_editor")
    def it_passes_content_from_editor_into_write_function(
        mock_get_input,
        mock_get_new_note_name,
        sqnotes_obj,
        mock_write_encrypted_note,
    ):
        mock_get_new_note_name.return_value = "test.txt.gpg"
        mock_get_input.return_value = "test content"
        mock_write_encrypted_note.return_value = True
        sqnotes_obj.new_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        assert called_kwargs["note_content"] == "test content"

    @pytest.mark.usefixtures(
        "mock_check_gpg_verified",
        "mock_get_configured_text_editor",
        "mock_open_database",
        "mock_is_use_ascii_armor",
        "mock_check_gpg_key_email",
        "mock_get_gpg_key_email",
        "mock_get_notes_dir_from_config",
        "mock_extract_and_save_keywords",
        "mock_check_text_editor_is_configured",
        "mock_commit_transaction",
        "mock_insert_new_note_into_database",
            "mock_get_is_initialized"
    )
    @patch.object(EncryptedNoteHelper, "write_encrypted_note")
    @patch.object(SQNotes, "_get_input_from_text_editor")
    def it_passes_new_note_name_into_write_function(
        mock_get_input,
        mock_write_encrypted_note,
        mock_get_new_note_name,
        sqnotes_obj,
        test_notes_directory,
    ):
        new_note_name = "test.txt.gpg"
        mock_get_new_note_name.side_effect = [new_note_name]
        mock_get_input.return_value = "test content"
        mock_write_encrypted_note.return_value = True
        sqnotes_obj.new_note()
        _, called_kwargs = mock_write_encrypted_note.call_args
        mock_write_encrypted_note.assert_called_once()
        expected_path = test_notes_directory / new_note_name
        assert (
            called_kwargs["note_file_path"]
            == str(expected_path)
        )

    @pytest.mark.usefixtures(
        "mock_check_gpg_verified",
        "mock_get_configured_text_editor",
        "mock_open_database",
        "mock_is_use_ascii_armor",
        "mock_check_gpg_key_email",
        "mock_get_gpg_key_email",
        "mock_get_notes_dir_from_config",
        "mock_extract_and_save_keywords",
        "mock_check_text_editor_is_configured",
        "mock_commit_transaction",
        "mock_insert_new_note_into_database",
            "mock_get_is_initialized"
    )
    @patch.object(SQNotes, "_get_input_from_text_editor", just_return("content"))
    @patch.object(EncryptedNoteHelper, "write_encrypted_note")
    def it_prints_message_saying_note_was_created(
        mock_write_encrypted_note,
        mock_get_new_note_name,
        mock_print,
        sqnotes_obj: SQNotes,
    ):
        base_filename = "test.txt.gpg"
        mock_get_new_note_name.side_effect = [base_filename]
        mock_write_encrypted_note.return_value = True
        sqnotes_obj.new_note()
        note_added_message = interface_copy.NOTE_ADDED().format(base_filename)
        output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
        assert note_added_message in output

    def describe_gpg_raises_exception():

        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_get_configured_text_editor",
            "mock_open_database",
            "mock_is_use_ascii_armor",
            "mock_check_gpg_key_email",
            "mock_get_gpg_key_email",
            "mock_get_notes_dir_from_config",
            "mock_extract_and_save_keywords",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_insert_new_note_into_database",
            "mock_get_is_initialized"
        )
        @patch.object(SQNotes, "_get_input_from_text_editor", just_return("content"))
        @patch.object(EncryptedNoteHelper, "write_encrypted_note")
        def it_exits(
            mock_write_encrypted_note, mock_get_new_note_name, sqnotes_obj: SQNotes
        ):
            mock_get_new_note_name.side_effect = ["test.txt.gpg"]
            mock_write_encrypted_note.side_effect = GPGSubprocessException()

            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()

        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_get_configured_text_editor",
            "mock_open_database",
            "mock_is_use_ascii_armor",
            "mock_check_gpg_key_email",
            "mock_get_gpg_key_email",
            "mock_get_notes_dir_from_config",
            "mock_extract_and_save_keywords",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_insert_new_note_into_database",
            "mock_get_is_initialized"
        )
        @patch.object(SQNotes, "_get_input_from_text_editor", just_return("content"))
        @patch.object(EncryptedNoteHelper, "write_encrypted_note")
        def it_prints_error_message(
            mock_write_encrypted_note,
            mock_get_new_note_name,
            sqnotes_obj: SQNotes,
            mock_print,
        ):
            mock_get_new_note_name.return_value = "test.txt.gpg"
            mock_write_encrypted_note.return_value = True
            mock_write_encrypted_note.side_effect = GPGSubprocessException()

            with pytest.raises(SystemExit):
                sqnotes_obj.new_note()
                output = get_all_mocked_print_output(mocked_print=mock_print)
                expected_message = interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
                assert expected_message in output
