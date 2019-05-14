#!/usr/bin/env python
''' commandline tool for loading in a datadump to the next stages of feateng.

TODO: fix --writecsv arg, it doesn't work.   '''

from argparse import ArgumentParser
import sys
from gvars import FILE_SIGNATURES, DUMP, TO_DROP
from load import Load
from logna import LogMissing


def get_args() -> ArgumentParser:
    ''' get arguments for commandline tool. '''
    parser: ArgumentParser = ArgumentParser(
        description='Load a datadump of multiple uniform-column\'d .csvs, run a couple cleaning and filtering functions, and write and/or return a df. ')

    parser.add_argument('--dumpname', type=str, default=DUMP,
                        help='the name dump you want to load. ')

    parser.add_argument(
        '--windows',
        nargs='+',
        type=str,
        default=FILE_SIGNATURES,
        help='list of file signatures you want to load')

    parser.add_argument(
        '--filename',
        type=str,
        help='name you would like for your output csv. ',
        default=DUMP +
        '-total')

    parser.add_argument(
        '--writecsv',
        type=bool,
        default=True,
        help="would you like to write output csv? if not, set to False. NOTE: currently not fully operational. ")

    parser.add_argument(
        '--logmissing',
        type=bool,
        default=True,
        help="would you like to record info about missingness? if not, set to False. ")

    return parser


parser = get_args()
args = parser.parse_args()


if __name__ == '__main__':
    try:
        load: Load = Load(args.dumpname, args.windows)

        missing_log: LogMissing = LogMissing(load)

        write: bool = bool(args.writecsv)

        logmissing: bool = bool(args.logmissing)

        if write:
            sys.stdout.write("writing...")
            load.export_csv(args.filename)
            sys.stdout.write("\r")
        else:
            print("not writing, but everything is fine. ")

        if logmissing:
            sys.stdout.write("writing missingness...")
            missing_log.export_csv()
            sys.stdout.write('\r')
            sys.stdout.write('\b')
            sys.stdout.write('\r')
    except Exception as e:
        print(" something is wrong. ")
        print(f"exception: {e}")
