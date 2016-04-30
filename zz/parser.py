import arrow
import parsley


class Record(object):
    def __init__(self):
        self.timestamp = None
        self.record_type = None
        self.comment = None
        self.tags = []

    @classmethod
    def _parse(cls, ts, entries):
        self = cls()
        self.timestamp = ts

        for entry_type, text in entries:
            if entry_type in ('begin', 'end'):
                if self.record_type is not None:
                    raise ValueError('Entry has more than one begin/end')

                self.record_type = entry_type
                self.comment = text
                continue

            if entry_type == 't':
                self.tags.append(text)
                continue

            raise NotImplementedError

        return self


def drop_after(line, char):
    idx = line.find(';')

    if idx != -1:
        return line[:idx]

    return line


def preprocess(s):
    return ('\n'.join(drop_after(line, ';').rstrip()
                      for line in s.splitlines()) + '\n')


ZZ_GRAMMAR = parsley.makeGrammar(r"""
ls = <' '+>
nls = ls* '\n'
text = <(anything:x ?(x not in '\n'))+>
indent = (' ' | '\t' ) ls*
date = <digit>{4}:y '-' <digit>{2}:m '-' <digit>{2}:d
    -> (int(''.join(y)),
        int(''.join(m)),
        int(''.join(d)))
time = <digit>{2}:h ':' <digit>{2}:m (':' <digit>{2})?:s
    -> (int(''.join(h)),
        int(''.join(m)),
        int(''.join(s or ['0'])))
timezone = (letterOrDigit | '+')+:tz -> ''.join(tz)
naive_dt = date:d ls time:t -> arrow.get(*(d+t))
aware_dt = naive_dt:dt ls timezone:tz
           -> arrow.get(dt.naive, tz)
timestamp = aware_dt:dt -> dt
entry = indent ('begin'|'end'|'t'):t ls text:tx nls -> (t, tx)
record = timestamp:ts nls
         entry+:entries -> Record._parse(ts, entries)
log = (matchrecord:m ws -> m)*:records
      -> records
""", {'arrow': arrow,
      'Record': Record})
