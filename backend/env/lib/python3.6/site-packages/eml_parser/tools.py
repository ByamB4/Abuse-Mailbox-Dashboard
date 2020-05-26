import re
import eml_parser


def loop_compare_list(element_a: list, element_b: list):
    for element_a_value in element_a:
        if not isinstance(element_a_value, str):
            # if the type of the element is not a string, we fuzzy look for an
            # identical element in the second object
            found = False
            for element_b_value in element_b:
                try:
                    recursive_compare(element_a_value, element_b_value)
                    print('\npuki-found-l\n', element_a_value, '\n', 50 * '>', '\n', element_b_value, '\n', 30 * '#', '\n')
                    found = True
                    break
                except AssertionError:
                    pass

            assert found, '\nElement not found in list:\n->{}\n->{}\n'.format(element_a_value, element_b)
        else:
            print('\npuki-l-compare\n', element_a_value, '\n', 50 * '>', '\n', element_b, '\n', 30 * '#', '\n')

            try:
                assert element_a_value in element_b
                print('\npuki-l-compare-found-1\n', element_a_value, '\n', 50 * '>', '\n', element_b, '\n', 30 * '#', '\n')
            except AssertionError:
                # ignore quotings, this should not trigger an exception
                test_value_a = re.sub(r'[\n\t"]', '', element_a_value.lstrip('.'))
                # @TODO remove me
                test_value_a = test_value_a.replace(' (UTC)', '')

                if '=?' in test_value_a:
                    test_value_a = eml_parser.decode.decode_field(test_value_a)

                test_value_b = ''
                found = False

                for element_b_value in element_b:
                    test_value_b = re.sub(r'[\n\t"]', '', element_b_value.lstrip('.'))
                    # @TODO remove me
                    test_value_b = test_value_b.replace(' (UTC)', '')

                    if '=?' in test_value_b:
                        test_value_b = eml_parser.decode.decode_field(test_value_b)

                    try:
                        assert test_value_a == test_value_b
                        found = True
                        break
                    except AssertionError:
                        pass

                assert found, '\npuki-1:\n->{}\n->{}\n'.format(test_value_a, test_value_b)

            # recursive_compare(element_a_value, element_b[element_b.index(test_value_a)])


def recursive_compare(element_a: dict, element_b: dict):
    '''Function for recursively comparing two variables and check if they are equal.
    The idea behind this function is to check two objects generated from JSON strings.
    Types which are supported by JSON are supported here as well.

    Args:
        element_a (dict): Object A to compare to object B.
        element_b (dict): Object B to compare to object A.

    Raises:
        AssertionError: Raises an AssertionError whenever differences are found while
                        comparing the objects.
    '''
    if isinstance(element_a, dict):
        assert isinstance(element_b, dict)

        for element_a_key, element_a_value in element_a.items():
            assert element_a_key in element_b

            recursive_compare(element_a_value, element_b[element_a_key])

    elif isinstance(element_a, list):
        assert isinstance(element_b, list)
        assert len(element_a) == len(element_b), 'non-identical length::\n->{}\n->{}\n'.format(element_a, element_b)

        print('FIRST :: orig')
        loop_compare_list(element_a, element_b)
        print('FIRST :: second')
        loop_compare_list(element_b, element_a)

    elif isinstance(element_a, (int, bool)) or element_a is None:
        assert type(element_a) is type(element_b)
        assert element_a == element_b

    elif isinstance(element_a, str):
        assert isinstance(element_b, str)

        try:
            assert element_a == element_a
        except AssertionError:
            loop_compare_list(element_a, element_b)
            print('\npuki-found\n', element_a, '\n', 50 * '>', '\n', element_b, '\n', 30 * '#', '\n')

    else:
        raise ValueError('No idea how to handle - {}'.format(type(element_a)))


def flatten(exp):
    def sub(exp, res):
        if type(exp) == dict:
            for k, v in exp.items():
                yield from sub(v, res+[k])
        elif type(exp) == list:
            for v in exp:
                yield from sub(v, res)
        elif exp is None:
            yield ("_".join(res), '')
        else:
            yield ("_".join(res), exp)


    flat_kv = {}
    for k, v in sub(exp, []):
        if not k in flat_kv:
            flat_kv[k] = [v]
        else:
            flat_kv[k].append(v)

    return flat_kv
