

import pytest
from unittest.mock import patch
from sqnotes import interface_copy
from test.test_helper import get_all_mocked_print_output_to_string, just_return,\
    get_all_mocked_print_output, get_all_single_arg_inputs, get_all_inputs_by_kw
from sqnotes.path_input_helper import PathInputHelper
from sqnotes.user_input_helper import UserInputHelper


# @pytest.fixture
# def mock_get_string_input():
#     with patch.object(UserInputHelper, ) as mock:
#         yield mock


@pytest.fixture
def mock_apple_input():
    with patch('builtins.input') as mock:
        mock.side_effect = ['apple' for _ in range(0,10)]
        yield mock

def describe_path_input_helper():


    def it_prompts_to_input_path(
                                    mock_path_input_helper,
                                     mock_input,
                                     mock_print
                                 ):
        mock_input.side_effect = ['some/path']
        mock_path_input_helper.get_path_interactive()
        output = get_all_mocked_print_output(mocked_print=mock_print)
        prompt = interface_copy.PROMPT_FOR_PATH()
        assert prompt in output

    def describe_input_is_blank():
    
        def describe_second_input_nonempty_string():
    
            @patch('builtins.input')
            @patch('builtins.print')
            def it_prompts_again(
                                    mock_print,
                                    mock_input,
                                    mock_path_input_helper
                                    ):
                mock_input.side_effect = ['', 'apple']
                mock_path_input_helper.get_path_interactive()
                output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                expected_prompt = interface_copy.PROMPT_FOR_PATH()
                number_of_promps = output.count(expected_prompt)
                assert number_of_promps == 2

    #
    #
    # def describe_first_input_is_a_nonempty_string():
    #
    #
    #     def describe_is_a_valid_path():
    #
    #         @patch('sqnotes.path_input_helper._is_a_valid_path')
    #         @patch('builtins.input')
    #         @patch('builtins.print')
    #         def it_checks_if_input_valid_path(
    #                                 mock_print,
    #                                 mock_input,
    #                                 mock_is_a_valid_path,
    #                                 mock_path_input_helper
    #                                 ):
    #             test_path = 'some/path/input'
    #             mock_is_a_valid_path.return_value = True
    #             mock_input.side_effect = [test_path]
    #             mock_path_input_helper.get_path_interactive()
    #             mock_is_a_valid_path.assert_called_once_with(input_string = test_path)
    #
    #     def describe_is_not_a_valid_path():
    #
    #         @patch('sqnotes.path_input_helper._is_a_valid_path')
    #         @patch('builtins.input')
    #         @patch('builtins.print')
    #         def it_prints_invalid_path_message (
    #                                                         mock_print,
    #                                                         mock_input,
    #                                                         mock_is_a_valid_path,
    #                                                         mock_path_input_helper
    #                                                         ):
    #             test_path = 'some/path/input'
    #             test_path2 = 'some/other/path/input'
    #             mock_is_a_valid_path.side_effect = [False, True]
    #             mock_input.side_effect = [test_path, test_path2]
    #             mock_path_input_helper.get_path_interactive()
    #             expected_message = interface_copy.PATH_INPUT_COULD_NOT_BE_VERIFIED().format(test_path)
    #             output = get_all_mocked_print_output(mocked_print=mock_print)
    #             assert expected_message in output
    #
    #

        
            
        