from zz import parser


def test_preprocess_normalizes_newlines():
    input = """hello\none\r\ntwo\nthree\n\n\n"""
    expected = """hello\none\ntwo\nthree\n\n\n"""

    assert expected == parser.preprocess(input)


def test_preprocess_strips_comments():
    input = """hello ; this is a comment\nworld!\r\n"""
    expected = """hello\nworld!\n"""

    assert expected == parser.preprocess(input)


def test_record_parse():
    input = ("2016-04-24 15:13:12 GMT+1\n"
             "  begin hacking on zz\n"
             "  t acc:do-not-bill\n"
             "  t inv:mbr-1\n")

    blk = parser.ZZ_GRAMMAR(input).record()

    # check naive date and timezone
    assert blk.timestamp.naive.timetuple()[:6] == (2016, 4, 24, 15, 13, 12)
    assert blk.timestamp.to('utc').naive.timetuple()[:6] == (2016, 4, 24, 14,
                                                             13, 12)

    assert blk.record_type == 'begin'
    assert blk.tags == ['acc:do-not-bill', 'inv:mbr-1']
