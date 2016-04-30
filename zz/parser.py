def drop_after(line, char):
    idx = line.find(';')

    if idx != -1:
        return line[:idx]

    return line


def preprocess(s):
    return '\n'.join(drop_after(line, ';') for line in s.splitlines()) + '\n'
