
import pytest
from unittest.mock import patch, Mock
from sqnotes.user_input_helper import UserInputHelper,\
    ValidationFailureException, VALIDATION_FAILURE_MESSAGE
from test.test_helper import get_all_mocked_print_output,\
    get_all_mocked_print_output_to_string



@pytest.fixture
def user_input_helper() -> UserInputHelper:
    user_input_helper = UserInputHelper()
    yield user_input_helper
    


    
def describe_user_input_helper():
    
    @patch('builtins.print')
    @patch('builtins.input')
    def it_prompts_user_with_specified_prompt(
                                            mock_input,
                                            mock_print,
                                            user_input_helper
                                                ):
        test_prompt = "test get input"
        test_user_input = 'apple'
        mock_input.side_effect = [test_user_input]
        user_input_helper.get_string_input(prompt = test_prompt)
        output = get_all_mocked_print_output(mocked_print=mock_print)
        assert test_prompt in output
        
        
    
    @patch('builtins.print')
    @patch('builtins.input')
    def it_passes_input_through_validator (
                                            mock_input,
                                            mock_print,
                                            user_input_helper
                                                ):
        test_prompt = "test get input"
        test_user_input = 'apple'
        validator = Mock()
        validator.side_effect = [True, True]
        mock_input.side_effect = [test_user_input, 'input2']
        user_input_helper.get_string_input(prompt = test_prompt, validator = validator)
        validator.assert_called_once_with(test_user_input)
        
        
    def describe_validation_fails():
        
        
        def describe_validation_failure_message_specified():
        
            @patch('builtins.print')
            @patch('builtins.input')
            def it_prints_validation_failure_message (
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper
                                                        ):
                test_prompt = "test get input"
                test_user_input = 'apple'
                validation_failure = 'validation failure message'
                validator = Mock()
                validator.side_effect = [False, True]
                mock_input.side_effect = [test_user_input, 'input2']
                user_input_helper.get_string_input(prompt = test_prompt, 
                                                       validator = validator,
                                                       validation_failure_message = validation_failure
                                                       )
                output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                assert validation_failure in output       
            
            @patch('builtins.print')
            @patch('builtins.input')
            def it_prompts_for_input_again (
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper
                                                        ):
                test_prompt = "test get input"
                test_user_input = 'apple'
                validation_failure = 'validation failure message'
                validator = Mock()
                validator.side_effect = [False, True]
                mock_input.side_effect = [test_user_input, 'input2']
                user_input_helper.get_string_input(prompt = test_prompt, 
                                                       validator = validator,
                                                       validation_failure_message = validation_failure
                                                       )
                output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                num_prompts = output.count(test_prompt)
                assert num_prompts == 2 
            
            
        def describe_validation_failure_not_specified():
        
            @patch('builtins.print')
            @patch('builtins.input')
            def it_prints_validation_failure_message (
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper
                                                        ):
                test_prompt = "test get input"
                test_user_input = 'apple'
                validator = Mock()
                validator.side_effect = [False, True]
                mock_input.side_effect = [test_user_input, 'input2']
                user_input_helper.get_string_input(prompt = test_prompt, 
                                                       validator = validator,
                                                       )
                output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                assert VALIDATION_FAILURE_MESSAGE in output       
            
        
        
        