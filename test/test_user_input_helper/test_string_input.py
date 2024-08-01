
import pytest
from unittest.mock import patch, Mock
from sqnotes.user_input_helper import UserInputHelper,\
    VALIDATION_FAILURE_MESSAGE,\
    ExceededMaxInputAttemptsException
from test.test_helper import get_all_mocked_print_output,\
    get_all_mocked_print_output_to_string



@pytest.fixture
def user_input_helper() -> UserInputHelper:
    user_input_helper = UserInputHelper()
    yield user_input_helper
    
@pytest.fixture
def mock_input():
    with patch('builtins.input') as mock:
        yield mock
        
@pytest.fixture
def mock_print():
    with patch('builtins.print') as mock:
        yield mock

@pytest.fixture
def mock_validator():
    validator = Mock()
    yield validator

    
test_prompt = "Specify some string.> "
second_user_input = "second input"
test_user_input = 'apple'
test_third_input = 'pear'
test_second_user_input = 'pear'
validation_failure = 'validation failure message'    

def describe_user_input_helper():
    

    def it_prompts_user_with_specified_prompt(
                                            mock_input,
                                            mock_print,
                                            user_input_helper
                                                ):
        test_user_input = 'apple'
        mock_input.side_effect = [test_user_input]
        user_input_helper.get_string_input(prompt = test_prompt)
        output = get_all_mocked_print_output(mocked_print=mock_print)
        assert test_prompt in output
        
        

    def it_passes_input_through_validator (
                                            mock_input,
                                            mock_print,
                                            user_input_helper
                                                ):
        test_user_input = 'apple'
        validator = Mock()
        validator.side_effect = [True, True]
        mock_input.side_effect = [test_user_input, 'input2']
        user_input_helper.get_string_input(prompt = test_prompt, validator = validator)
        validator.assert_called_once_with(test_user_input)
        
        
    def describe_validation_passes():
        
        def it_returns_input(
                                mock_input,
                                mock_print,
                                user_input_helper
                                ):
            test_user_input = 'apple'
            validation_failure = 'validation failure message'
            validator = Mock()
            validator.side_effect = [True, True]
            mock_input.side_effect = [test_user_input, second_user_input]
            result = user_input_helper.get_string_input(prompt = test_prompt, 
                                                   validator = validator,
                                                   validation_failure_message = validation_failure
                                                   )
            assert result == test_user_input
        
        
    def describe_validation_fails():
        
        
        def describe_validation_failure_message_specified():
            
            
            def describe_input_is_blank():
                
                def it_prints_validation_failure_message_with_blank(
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper,
                                                    mock_validator
                                                    ):
                    empty_input_input = ''
                    mock_validator.side_effect = [False, True]
                    mock_input.side_effect = [empty_input_input, second_user_input]
                    validator_failure_message = 'test with {}'
                    expected_failure_message = "test with ''"
                    
                    user_input_helper.get_string_input(prompt = test_prompt, 
                                                           validator = mock_validator,
                                                           validation_failure_message = validator_failure_message
                                                        )
                    
                    output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                    assert expected_failure_message in output    
            
        
            def it_prints_validation_failure_message (
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper
                                                        ):
                test_user_input = 'apple'
                validation_failure = VALIDATION_FAILURE_MESSAGE.format(test_user_input)
                validator = Mock()
                validator.side_effect = [False, True]
                mock_input.side_effect = [test_user_input, 'input2']
                
                
                user_input_helper.get_string_input(prompt = test_prompt, 
                                                       validator = validator,
                                                       validation_failure_message = validation_failure
                                                       )
                output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                assert validation_failure in output       
            
            def it_prompts_for_input_again (
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper
                                                        ):
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
            
            
            def describe_second_attempt_passes_validation():
                
                
                def it_returns_second_input(
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper
                                                    ):
                    test_user_input = 'apple'
                    validation_failure = 'validation failure message'
                    validator = Mock()
                    validator.side_effect = [False, True]
                    mock_input.side_effect = [test_user_input, second_user_input]
                    result = user_input_helper.get_string_input(prompt = test_prompt, 
                                                           validator = validator,
                                                           validation_failure_message = validation_failure
                                                           )
                    assert result == second_user_input
                    
            
        def describe_validation_failure_not_specified():
        
            def it_prints_validation_failure_message (
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper,
                                                    mock_validator
                                                    ):
                test_user_input = 'apple'
                mock_validator.side_effect = [False, True]
                mock_input.side_effect = [test_user_input, 'input2']
                message = VALIDATION_FAILURE_MESSAGE.format(test_user_input)
                user_input_helper.get_string_input(prompt = test_prompt, 
                                                       validator = mock_validator,
                                                    )
                output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                assert message in output       
            
        
        def describe_limit_attempts_is_2():
            
            attempt_limit = 2
            
            def describe_validation_passes_first_attmept():
                
                def it_returns_input(
                                        mock_input,
                                        mock_print,
                                        user_input_helper,
                                        attempt_limit = attempt_limit
                                        ):
                    
                    validation_failure = 'validation failure message'
                    validator = Mock()
                    validator.side_effect = [True, True]
                    mock_input.side_effect = [test_user_input, second_user_input]
                    result = user_input_helper.get_string_input(prompt = test_prompt, 
                                                           validator = validator,
                                                           validation_failure_message = validation_failure,
                                                           attempt_limit = attempt_limit
                                                           )
                    assert result == test_user_input
            
            
            def describe_validation_fails():
            
            
                def describe_second_input_valid():
                
                    def it_prompts_for_input_again (
                                                                mock_input,
                                                                mock_print,
                                                                user_input_helper,
                                                                mock_validator
                                                                    ):
                        mock_validator.side_effect = [False, True]
                        mock_input.side_effect = [test_user_input, test_second_user_input]
                        user_input_helper.get_string_input(prompt = test_prompt, 
                                                               validator = mock_validator,
                                                               validation_failure_message = validation_failure,
                                                               attempt_limit = attempt_limit
                                                               )
                        output = get_all_mocked_print_output_to_string(mocked_print=mock_print)
                        num_prompts = output.count(test_prompt)
                        assert num_prompts == 2 
            
            
            
            
                    def it_returns_second_input(
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper,
                                                    mock_validator
                                                    ):
                        mock_validator.side_effect = [False, True]
                        mock_input.side_effect = [test_user_input, second_user_input]
                        result = user_input_helper.get_string_input(prompt = test_prompt, 
                                                               validator = mock_validator,
                                                               validation_failure_message = validation_failure,
                                                               attempt_limit = attempt_limit
                                                               )
                        assert result == second_user_input
            
                def describe_second_input_fails_validation():
                    
                    
                    def it_raises_ExceededMaxInputAttemptsException (
                                                                mock_input,
                                                                mock_print,
                                                                user_input_helper,
                                                                mock_validator
                                                                    ):
                        mock_validator.side_effect = [False, False]
                        mock_input.side_effect = [test_user_input, test_second_user_input]
                        with pytest.raises(ExceededMaxInputAttemptsException):
                            user_input_helper.get_string_input(prompt = test_prompt, 
                                                               validator = mock_validator,
                                                               validation_failure_message = validation_failure,
                                                               attempt_limit = attempt_limit
                                                               )
                        
        def describe_attempt_limit_is_3():
                      
                    
            attempt_limit = 3
            
            def describe_first_two_attempts_fail():
                
                def describe_third_attempt_fails():
            
                    def it_raises_ExceededMaxInputAttemptsException (
                                                                mock_input,
                                                                mock_print,
                                                                user_input_helper,
                                                                mock_validator
                                                                ):
                        mock_validator.side_effect = [False, False, False]
                        mock_input.side_effect = [test_user_input, test_second_user_input, test_third_input]
                        with pytest.raises(ExceededMaxInputAttemptsException):
                            user_input_helper.get_string_input(prompt = test_prompt, 
                                                               validator = mock_validator,
                                                               validation_failure_message = validation_failure,
                                                               attempt_limit = attempt_limit
                                                               )
                        
        
                def describe_third_attempt_passes():
                    
                    def it_returns_third_input(
                                                    mock_input,
                                                    mock_print,
                                                    user_input_helper,
                                                    mock_validator
                                                    ):
                        mock_validator.side_effect = [False, False, True]
                        mock_input.side_effect = [test_user_input, second_user_input, test_third_input]
                        result = user_input_helper.get_string_input(prompt = test_prompt, 
                                                               validator = mock_validator,
                                                               validation_failure_message = validation_failure,
                                                               attempt_limit = attempt_limit
                                                               )
                        assert result == test_third_input
                    
        