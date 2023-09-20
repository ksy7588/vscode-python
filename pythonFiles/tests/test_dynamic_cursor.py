import importlib
import textwrap

import normalizeSelection


def test_dictionary_mouse_mover():
    """
    Having the mouse cursor on second line,
    'my_dict = {'
    and pressing shift+enter should bring the
    mouse cursor to line 6, on and to be able to run
    'print('only send the dictionary')'
    """
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        not_dictionary = 'hi'
        my_dict = {
            "key1": "value1",
            "key2": "value2"
        }
        print('only send the dictionary')
        """
    )

    result = normalizeSelection.traverse_file(src, 2, 2, False)

    assert result["which_line_next"] == 6


def test_beginning_func():
    """
    Pressing shift+enter on the very first line,
    of function definition, such as 'my_func():'
    It should properly skip the comment and assert the
    next executable line to be executed is line 5 at
    'my_dict = {'
    """
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        def my_func():
            print("line 2")
            print("line 3")
        # Skip line 4 because it is a comment
        my_dict = {
            "key1": "value1",
            "key2": "value2"
        }
        """
    )

    result = normalizeSelection.traverse_file(src, 1, 1, False)

    assert result["which_line_next"] == 5


def test_cursor_forloop():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        lucid_dream = ["Corgi", "Husky", "Pomsky"]
        for dogs in lucid_dream: # initial starting position
            print(dogs)
            print("I wish I had a dog!")

        print("This should be the next block that should be ran")
        """
    )

    result = normalizeSelection.traverse_file(src, 2, 2, False)

    assert result["which_line_next"] == 6


def test_inside_forloop():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        for food in lucid_dream:
            print("We are starting") # initial starting position
            print("Next cursor should be here!")

        """
    )

    result = normalizeSelection.traverse_file(src, 2, 2, False)

    assert result["which_line_next"] == 3


def test_skip_sameline_statements():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        print("Audi");print("BMW");print("Mercedes")
        print("Next line to be run is here!")
        """
    )
    result = normalizeSelection.traverse_file(src, 1, 1, False)

    assert result["which_line_next"] == 2


def test_skip_multi_comp_lambda():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        (
        my_first_var
        for my_first_var in range(1, 10)
        if my_first_var % 2 == 0
        )

        my_lambda = lambda x: (
            x + 1
        )
        """
    )

    result = normalizeSelection.traverse_file(src, 1, 1, False)
    # Shift enter from the very first ( should make
    # next executable statement as the lambda expression
    assert result["which_line_next"] == 7

