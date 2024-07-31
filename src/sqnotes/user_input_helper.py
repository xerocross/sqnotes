


VALIDATION_FAILURE_MESSAGE = 'Input {} failed validation.'
class ValidationFailureException(Exception):
    """Raise if input fails user-input validation function."""


class UserInputHelper:

    @staticmethod
    def get_string_input(prompt, 
                         validator = None, 
                         validation_failure_message = None):
        user_input = None
        while True:
            print(prompt)
            user_input = input()
            if validator is not None:
                is_valid = validator(user_input)
                if not is_valid:
                    if validation_failure_message is not None:
                        print(validation_failure_message)
                    else:
                        print(VALIDATION_FAILURE_MESSAGE)
                else:
                    break
            else:
                break
        return user_input