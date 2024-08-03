import pytest
from sqnotes.sqnotes_module import SQNotes, GPGSubprocessException
from test.test_helper import (
    get_all_mocked_print_output,
    get_all_mocked_print_output_to_string,
)
from sqnotes import interface_copy


def describe_search_notes():

    def describe_given_one_search_term():

        @pytest.mark.usefixtures(
            "mock_get_notes_dir_from_config", "mock_get_all_note_paths"
        )
        def it_prints_notes_that_match_search_term(
            mock_print, mock_get_decrypted_content_in_memory, sqnotes_obj: SQNotes
        ):
            search_queries = ["apple"]
            mock_get_decrypted_content_in_memory.side_effect = [
                "a note with apple in it",
                "a second note with apple in it",
                "a note without the search term",
            ]
            sqnotes_obj.search_notes(search_queries=search_queries)
            mock_print.assert_called()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            assert "a note with apple" in output
            assert "a second note with apple" in output
            assert not "a note without the search term" in output

    def describe_given_two_search_terms():

        @pytest.mark.usefixtures(
            "mock_get_notes_dir_from_config", "mock_get_all_note_paths"
        )
        def it_prints_notes_that_match_search_terms(
            mock_print, mock_get_decrypted_content_in_memory, sqnotes_obj: SQNotes
        ):
            search_queries = ["apple", "pear"]
            first_note = "a note with apple in it"
            second_note = "a second note with apple and pear in it"
            third_note = "a note without the search term"
            mock_get_decrypted_content_in_memory.side_effect = [
                first_note,
                second_note,
                third_note,
            ]
            sqnotes_obj.search_notes(search_queries=search_queries)
            mock_print.assert_called()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            assert not first_note in output
            assert second_note in output
            assert not third_note in output

    def describe_gpg_raises_exception():

        @pytest.mark.usefixtures(
            "mock_get_notes_dir_from_config", "mock_get_all_note_paths", "mock_print"
        )
        def it_exits_with_GPG_Error(
            mock_get_decrypted_content_in_memory, sqnotes_obj: SQNotes
        ):
            search_queries = ["apple", "pear"]
            mock_get_decrypted_content_in_memory.side_effect = GPGSubprocessException()
            with pytest.raises(SystemExit) as excinfo:
                sqnotes_obj.search_notes(search_queries=search_queries)
            assert excinfo.value.code == sqnotes_obj.GPG_ERROR

        @pytest.mark.usefixtures(
            "mock_get_notes_dir_from_config", "mock_get_all_note_paths"
        )
        def it_prints_error_message(
            mock_get_decrypted_content_in_memory, sqnotes_obj, mock_print_to_so
        ):
            search_queries = ["apple", "pear"]
            mock_get_decrypted_content_in_memory.side_effect = GPGSubprocessException()
            with pytest.raises(SystemExit):
                sqnotes_obj.search_notes(search_queries=search_queries)
            output = get_all_mocked_print_output_to_string(
                mocked_print=mock_print_to_so
            )
            expected_message = (
                interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
                + " "
                + interface_copy.EXITING()
            )
            assert expected_message in output
