from unittest.mock import patch

import pytest

from sqnotes.encrypted_note_helper import EncryptedNoteHelper, GPGSubprocessException

from test.test_helper import (
    get_all_mocked_print_output,
    get_all_mocked_print_output_to_string,
)
from sqnotes.sqnotes_module import SQNotes
from sqnotes import interface_copy


def describe_directly_insert_note():

    @pytest.mark.usefixtures(
        "mock_insert_new_note_into_database",
        "mock_is_use_ascii_armor",
        "mock_open_database",
        "mock_check_gpg_verified",
        "mock_commit_transaction",
        "mock_get_gpg_key_email",
        "mock_get_gpg_key_email",
        "mock_get_notes_dir_from_config",
        "mock_get_new_note_name",
        "mock_extract_and_save_keywords",
    )
    @patch.object(EncryptedNoteHelper, "write_encrypted_note")
    def it_passes_note_content_into_write_function(
        mock_write_encrypted_note, sqnotes_obj: SQNotes
    ):

        test_direct_input = "a note about #apples"
        sqnotes_obj.directly_insert_note(text=test_direct_input)
        mock_write_encrypted_note.assert_called_once()
        first_call = mock_write_encrypted_note.call_args_list[0]
        _, first_call_kwargs = first_call
        assert first_call_kwargs["note_content"] == test_direct_input

    def describe_exception_on_opening_database():

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_open_database",
            "mock_write_encrypted_note",
            "mock_insert_new_note_into_database",
            "mock_get_configured_text_editor",
            "mock_get_notes_dir_from_config",
        )
        @patch.object(SQNotes, "open_database")
        def it_exits(mock_open_database, sqnotes_obj: SQNotes):
            mock_open_database.side_effect = Exception()
            test_direct_input = "a note about #apples"
            with pytest.raises(SystemExit):
                sqnotes_obj.directly_insert_note(text=test_direct_input)

        @pytest.mark.usefixtures(
            "mock_check_gpg_key_email",
            "mock_is_use_ascii_armor",
            "mock_get_configured_text_editor",
            "mock_check_gpg_verified",
            "mock_check_text_editor_is_configured",
            "mock_commit_transaction",
            "mock_extract_and_save_keywords",
            "mock_get_new_note_name",
            "mock_get_gpg_key_email",
            "mock_open_database",
            "mock_write_encrypted_note",
            "mock_insert_new_note_into_database",
            "mock_get_configured_text_editor",
            "mock_get_notes_dir_from_config",
        )
        @patch.object(SQNotes, "open_database")
        def it_prints_error_message(
            mock_open_database, sqnotes_obj: SQNotes, mock_print
        ):
            mock_open_database.side_effect = Exception()
            test_direct_input = "a note about #apples"
            with pytest.raises(SystemExit):
                sqnotes_obj.directly_insert_note(text=test_direct_input)
                output = get_all_mocked_print_output(mocked_print=mock_print)
                expected_message = interface_copy.COULD_NOT_OPEN_DATABASE()
                exiting_message = interface_copy.EXITING()
                assert expected_message in output
                assert exiting_message in output

    def describe_gpg_exception_on_write():

        @pytest.mark.usefixtures(
            "mock_insert_new_note_into_database",
            "mock_is_use_ascii_armor",
            "mock_open_database",
            "mock_check_gpg_verified",
            "mock_commit_transaction",
            "mock_get_gpg_key_email",
            "mock_get_gpg_key_email",
            "mock_get_notes_dir_from_config",
            "mock_get_new_note_name",
            "mock_extract_and_save_keywords",
        )
        @patch.object(EncryptedNoteHelper, "write_encrypted_note")
        def it_exits(mock_write_encrypted_note, sqnotes_obj: SQNotes):
            """
            If encounters a GPGSubprocessException during writing
            encrypted note, application exits.
            """
            mock_write_encrypted_note.side_effect = GPGSubprocessException()

            test_direct_input = "a note about #apples"
            with pytest.raises(SystemExit) as excinfo:
                sqnotes_obj.directly_insert_note(text=test_direct_input)
            assert excinfo.value.code == sqnotes_obj.GPG_ERROR

        @pytest.mark.usefixtures(
            "mock_insert_new_note_into_database",
            "mock_is_use_ascii_armor",
            "mock_open_database",
            "mock_check_gpg_verified",
            "mock_commit_transaction",
            "mock_get_gpg_key_email",
            "mock_get_gpg_key_email",
            "mock_get_notes_dir_from_config",
            "mock_get_new_note_name",
            "mock_extract_and_save_keywords",
        )
        @patch.object(EncryptedNoteHelper, "write_encrypted_note")
        def it_prints_error_message(
            mock_write_encrypted_note, sqnotes_obj: SQNotes, mock_print_to_so
        ):
            mock_write_encrypted_note.side_effect = GPGSubprocessException()

            test_direct_input = "a note about #apples"
            with pytest.raises(SystemExit):
                sqnotes_obj.directly_insert_note(text=test_direct_input)
            output = get_all_mocked_print_output_to_string(
                mocked_print=mock_print_to_so
            )
            expected_message = (
                interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
                + " "
                + interface_copy.EXITING()
            )
            assert expected_message in output
