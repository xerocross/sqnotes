
def get_all_mocked_print_output(mocked_print):
    call_args = mocked_print.call_args_list
    arguments_list = [args[0] for args, _ in call_args]
    all_outtext = " ".join(arguments_list)
    return all_outtext

def get_all_single_arg_inputs(mocked_fn):
    call_args = mocked_fn.call_args_list
    arguments_list = [args[0] for args, _ in call_args]
    return arguments_list

def do_nothing(*args, **kwargs):
    pass

def get_true(*args, **kwargs):
    return True