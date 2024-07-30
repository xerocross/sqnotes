
import textwrap
import shutil

MAX_WIDTH = 70

def get_wrapped_text(input_text):
    width = get_text_width()
    wrapper = textwrap.TextWrapper(width=width, expand_tabs=False, replace_whitespace=False)
    paragraphs = input_text.split('\n\n')
    # print("paragraphs:")
    # print(paragraphs)
    wrapped_text = ''
    last_paragraph_index = len(paragraphs) - 1
    for i, paragraph in enumerate(paragraphs):
        wrapped_text += '\n'.join(wrapper.wrap(paragraph))
        if i != last_paragraph_index:
            wrapped_text += '\n\n'
    return wrapped_text


def get_text_width():
    return min(MAX_WIDTH, get_terminal_size())

def get_terminal_size():
    return shutil.get_terminal_size().columns