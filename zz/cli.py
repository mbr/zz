#!/usr/bin/python3

import datetime
import re
import os
from warnings import warn

import click

from . import parser

DEFAULT_ZZ_FILE = os.path.expanduser('~/.zz-timesheet')


class Block(object):
    def __init__(self):
        self.block_type = None
        self.timestamp = None
        self.msg = ''
        self.tags = []

    def is_complete(self):
        return self.block_type and self.timestamp

    def is_empty(self):
        return not (self.block_type or self.timestamp or self.tags or self.msg)

    def __str__(self):
        return ('{self.timestamp} {self.block_type} {self.tags} {self.msg}'
                .format(self=self))


class TimeSheetParseError(Exception):
    def __init__(self, msg, lineno=None, path=None):
        super(TimeSheetParseError, self).__init__(msg)
        self.lineno = lineno
        self.path = path

    def __str__(self):
        msg = super(TimeSheetParseError, self).__str__()
        if self.path and self.lineno:
            return '{}, line {}: {}'.format(self.path, self.lineno, msg)
        return msg


class TimeSheet(object):
    TIMESTAMP_RE = re.compile(r'^(?:(\d{4}-\d{2}-\d{2})\s+)?'
                              r'(\d{2}:\d{2}(?::\d{2})?)\s+'
                              r'(.*)?$')

    def __init__(self, path):
        self.path = path
        self.reload()

    def reload(self):
        blocks = []
        block = Block()

        if os.path.exists(self.path):

            with open(self.path) as src:
                buf = src.read() + '\n\n'  # extra nl to ensure last block is
                # finished
                buf = parser.preprocess(buf)

            for lineno, line in enumerate(buf.splitlines(), 1):
                if not line.strip():
                    # blank line, terminates timestamped block
                    if not block.is_empty():
                        if not block.is_complete():
                            raise TimeSheetParseError(
                                'Incomplete previous block',
                                lineno=lineno,
                                path=self.path)
                        blocks.append(block)
                        block = Block()
                    continue

                if not block.timestamp and line[0].isspace():
                    raise TimeSheetParseError('Expected timestamp.',
                                              lineno=lineno,
                                              path=self.path)

                # check if it's a timestamp
                m = self.TIMESTAMP_RE.match(line)
                if m:
                    date_s = m.group(1)
                    time_s = m.group(2)

                    tz_s = m.group(3).strip()

                    if tz_s:
                        warn('timezones not implemented at the moment')

                    # FIXME: switch to arrow
                    # parse date first
                    if not date_s:
                        if not blocks or not blocks[-1].timestamp:
                            raise TimeSheetParseError('Missing date',
                                                      lineno=lineno,
                                                      path=self.path)
                        tt_date = list(blocks[-1].timestamp.date().timetuple(
                        )[:3])
                    else:
                        tt_date = [int(v) for v in date_s.split('-')]

                    # time next
                    tt_time = [int(v) for v in time_s.split(':')]

                    block.timestamp = datetime.datetime(*(tt_date + tt_time))

                # it's a block input
                line = line.strip()
                if line.startswith('begin'):
                    if block.block_type:
                        raise TimeSheetParseError('Extra begin',
                                                  lineno=lineno,
                                                  path=self.path)
                    block.block_type = 'begin'
                    block.msg = line[5:].strip()
                elif line.startswith('end'):
                    if block.block_type:
                        raise TimeSheetParseError('Extra end',
                                                  lineno=lineno,
                                                  path=self.path)
                    block.block_type = 'end'
                else:
                    block.tags.append(line)

        self.blocks = blocks


@click.group()
@click.option('-f',
              '--file',
              'tsfile',
              type=click.Path(writable=True,
                              dir_okay=False),
              default=DEFAULT_ZZ_FILE,
              help='Timesheet file to use')
@click.pass_context
def cli(ctx, tsfile):
    click.echo('Using timesheet file: {}'.format(tsfile))
    ctx.obj = TimeSheet(tsfile)


@cli.command(help='List timesheet contents')
@click.pass_obj
def show(ts):
    for block in ts.blocks:
        print(block)


@cli.command(help='Begin a new task')
@click.pass_obj
def begin(ts):
    raise NotImplementedError


@cli.command(help='End the current task')
@click.pass_obj
def end(ts):
    raise NotImplementedError
