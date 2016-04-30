from zz import parser


def test_preprocess_normalizes_newlines():
    input = """hello\none\r\ntwo\nthree\n\n\n"""
    expected = """hello\none\ntwo\nthree\n\n\n"""

    assert expected == parser.preprocess(input)
