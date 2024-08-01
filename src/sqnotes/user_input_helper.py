
VALIDATION_FAILURE_MESSAGE = 'Input {} failed validation.'
class ValidationFailureException(Exception):
    """Raise if input fails user-input validation function."""

class ExceededMaxInputAttemptsException(Exception):
    """Raise if exceeds max number of allowed input attempts."""


class UserInputHelper:

    @staticmethod
    def get_string_input(prompt, 
                         validator = None, 
                         validation_failure_message = None,
                         attempt_limit = None):
        user_input = None
        attempt_number = 0
        
        if validator is not None:
            if validation_failure_message is not None:
                pre_format_validation_failure_message = validation_failure_message
            else:
                pre_format_validation_failure_message = VALIDATION_FAILURE_MESSAGE
        
        while True:
            attempt_number += 1
            if attempt_limit is not None:
                if attempt_number > attempt_limit:
                    raise ExceededMaxInputAttemptsException(f"Exceeded {attempt_limit} attempts.")
            
            
            print(prompt, end='')
            user_input = input()
            if validator is not None:
                is_valid = validator(user_input)
                if not is_valid:
                    message = pre_format_validation_failure_message
                    if '{}' in pre_format_validation_failure_message:
                        input_slug = "''" if user_input == '' else user_input
                        message = message.format(input_slug)
                    print(message)
                else:
                    break
            else:
                break
        return user_input