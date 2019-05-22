''' load data

dependent on gvars.py, for important information pertaining to the dump '''
import sys
from typing import List, Any, Union, Iterator, Optional
from tqdm import tqdm  # type: ignore
import pandas as pd  # type: ignore
# from pandarallel import pandarallel # type: ignore
# pandarallel.initialize()

from gvars import FILE_SIGNATURES, DUMP, TO_DROP, TO_KEEP, TARGET


class Load:
    def __init__(self, dump: str,
                 file_signatures: List[str],
                 to_drop: List[str] = TO_DROP,
                 to_keep: List[str] = TO_KEEP,
                 to_target: str = TARGET):
        ''' When you get a fresh dump, ensure that it's all in a directory

        '''
        self.dump: str = dump
        self.file_signatures: List[str] = file_signatures
        self.to_drop: List[str] = to_drop
        self.to_keep: List[str] = to_keep
        self.target: List[str] = [to_target]
        self.df: pd.DataFrame = pd.concat(
            self.df_iter_by_window(
                self.file_signatures))

    def csv_path(self, code: str) -> str:
        ''' takes a signature xxx-yyy
        meaning "sales closed between dumpdate-xxx and dumpdate-yyy"
        and returns the path to its csv.
        '''
        return ''.join(
            [self.dump, '/', self.dump, '-dump-', code, '.csv'])

    def clean_(self, dat: pd.DataFrame) -> pd.DataFrame:
        ''' Just drops the features we know we dont want
        and removes spaces and caps from feature names'''

        def try_num(x: Any) -> Union[float, Any]:
            ''' strip out spaces and dollar signs, handle commas from thousands places, cast to float. if fail, identity func. '''
            try:
                return float(x.replace(',', '')
                              .replace('$', '')
                              .replace(' ', ''))
            except ValueError as e:
                return x

        try:
            return (dat
                    .rename(columns=lambda s: s.replace(' ', '_')
                                               .replace('-', '_')
                                               .replace('.', '_')
                                               .lower())
                    # .drop(self.to_drop, axis=1)
                    #[self.to_keep + self.target]
                    .applymap(try_num))

        except Exception as e:
            print("fail: inspect input csvs and gvars.TO_DROP")
            print("exception: ", e)

    def df_iter_by_window(
            self, windows: List[str] = FILE_SIGNATURES) -> Iterator[pd.DataFrame]:
        ''' makes a dataframe from each file in data dump
        returns iterator'''
        for window in tqdm(windows, desc="cleaning & concatting..."):
            #sys.stdout.write("currently on " + self.csv_path(window))
            try:
                yield self.clean_(pd.read_csv(self.csv_path(window), low_memory=False))
            except Exception as e:
                print(f"fail: inspect input {window}.csv. ")

    def export_csv(self, name: Optional[str] = None, to_subdir: bool = True):
        '''will automatically add '.csv' to filename

        to_subdir argument puts it in playground
        TODO: implement alternative subdir argument.
        '''

        subdir: str = 'playground'
        path: str = '.csv'
        if name is not None:
            path = name + path
        else:
            path = self.dump + '-total' + path

        if to_subdir:
            path = '/'.join([subdir, path])

        try:
            self.df.to_csv(path_or_buf=path, index=False)
            sys.stdout.write("WROTE file")
            sys.stdout.write("\b")
        except Exception as e:
            print(e)
        finally:
            pass
