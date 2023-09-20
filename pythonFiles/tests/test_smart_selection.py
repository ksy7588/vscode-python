import importlib
import textwrap

import normalizeSelection


def test_part_dictionary():
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

    expected = textwrap.dedent(
        """\
        my_dict = {
            "key1": "value1",
            "key2": "value2"
        }
        """
    )

    result = normalizeSelection.traverse_file(src, 3, 3, False)
    assert result["normalized_smart_result"] == expected


def test_smart_shift_enter_multiple_statements():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        import textwrap
        import ast

        print("Porsche")
        print("Genesis")


        print("Audi");print("BMW");print("Mercedes")

        print("dont print me")

        """
    )
    # Expected to printing statement line by line,
    # for when multiple print statements are ran
    # from the same line.
    expected = textwrap.dedent(
        """\
        print("Audi")
        print("BMW")
        print("Mercedes")
        """
    )
    result = normalizeSelection.traverse_file(src, 8, 8, False)
    assert result["normalized_smart_result"] == expected


def test_two_layer_dictionary():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        print("dont print me")

        two_layered_dictionary = {
            'inner_dict_one': {
                'Audi': 'Germany',
                'BMW': 'Germnay',
                'Genesis': 'Korea',
            },
            'inner_dict_two': {
                'Mercedes': 'Germany',
                'Porsche': 'Germany',
                'Lamborghini': 'Italy',
                'Ferrari': 'Italy',
                'Maserati': 'Italy'
            }
        }
        """
    )
    expected = textwrap.dedent(
        """\
        two_layered_dictionary = {
            'inner_dict_one': {
                'Audi': 'Germany',
                'BMW': 'Germnay',
                'Genesis': 'Korea',
            },
            'inner_dict_two': {
                'Mercedes': 'Germany',
                'Porsche': 'Germany',
                'Lamborghini': 'Italy',
                'Ferrari': 'Italy',
                'Maserati': 'Italy'
            }
        }
        """
    )
    result = normalizeSelection.traverse_file(src, 6, 7, False)

    assert result["normalized_smart_result"] == expected


def test_run_whole_func():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        print("Decide which dog you will choose")
        def my_dogs():
            print("Corgi")
            print("Husky")
            print("Corgi2")
            print("Husky2")
            print("no dogs")
        """
    )

    expected = textwrap.dedent(
        """\
        def my_dogs():
            print("Corgi")
            print("Husky")
            print("Corgi2")
            print("Husky2")
            print("no dogs")

        """
    )
    result = normalizeSelection.traverse_file(src, 2, 2, False)

    assert result["normalized_smart_result"] == expected


def test_small_forloop():
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        for i in range(1, 6):
            print(i)
            print("Please also send this print statement")
        """
    )
    expected = textwrap.dedent(
        """\
        for i in range(1, 6):
            print(i)
            print("Please also send this print statement")

        """
    )

    # Cover the whole for loop block with multiple inner statements
    # Make sure to contain all of the print statements included.
    result = normalizeSelection.traverse_file(src, 1, 1, False)

    assert result["normalized_smart_result"] == expected


def inner_for_loop_component():
    """
    Pressing shift+enter inside a for loop,
    specifically on a viable expression
    by itself, such as print(i)
    should only return that exact expression
    """
    importlib.reload(normalizeSelection)
    src = textwrap.dedent(
        """\
        for i in range(1, 6):
            print(i)
            print("Please also send this print statement")
        """
    )
    result = normalizeSelection.traverse_file(src, 2, 2, False)
    expected = textwrap.dedent(
        """\
            print(i)
            """
    )

    assert result["normalized_smart_result"] == expected


def test_dict_comprehension():
    """
    Having the mouse cursor on the first line,
    and pressing shift+enter should return the
    whole dictionary comp, respecting user's code style.
    """

    importlib.reload
    src = textwrap.dedent(
        """\
        my_dict_comp = {temp_mover:
        temp_mover for temp_mover in range(1, 7)}
        """
    )

    expected = textwrap.dedent(
        """\
        my_dict_comp = {temp_mover:
        temp_mover for temp_mover in range(1, 7)}
        """
    )

    result = normalizeSelection.traverse_file(src, 1, 1, False)

    assert result["normalized_smart_result"] == expected


def test_send_whole_generator():
    """
    Pressing shift+enter on the first line, which is the '('
    should be returning the whole generator expression instead of just the '('
    """

    importlib.reload
    src = textwrap.dedent(
        """\
        (
            my_first_var
            for my_first_var in range(1, 10)
            if my_first_var % 2 == 0
        )
        """
    )

    expected = textwrap.dedent(
        """\
        (
            my_first_var
            for my_first_var in range(1, 10)
            if my_first_var % 2 == 0
        )

        """
    )

    result = normalizeSelection.traverse_file(src, 1, 1, False)

    assert result["normalized_smart_result"] == expected


def test_multiline_lambda():
    """
    Shift+enter on part of the lambda expression
    should return the whole lambda expression,
    regardless of whether all the component of
    lambda expression is on the same or not.
    """

    importlib.reload
    src = textwrap.dedent(
        """\
        my_lambda = lambda x: (
            x + 1
        )
        """
    )
    expected = textwrap.dedent(
        """\
        my_lambda = lambda x: (
            x + 1
        )

        """
    )

    result = normalizeSelection.traverse_file(src, 1, 1, False)
    assert result["normalized_smart_result"] == expected
