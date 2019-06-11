#!/usr/bin/env python

from typing import Tuple, Optional
import sys
from load import Load  # type: ignore
import pandas as pd  # type: ignore
from tqdm import tqdm  # type: ignore
from numpy import divide  # type: ignore
from typing import List, Dict, Optional, Tuple


class LogMissing:
    ''' log info about missingness: .
       1. report rates/percentages
       2. report list of correlates (collinearity tests w VIF?)
       3. report possible MAR-correlates (the Missing At Random missingness regime, meaning a feature's missingness is a function of other features. ) 
    '''

    def __init__(self, load: Load, correlation_strength: float = 0.8):
        self.loader: Load = load
        assert 0 < correlation_strength < 1, "select correlation magnitude between 0 and 1"
        self.correlation_strength: float = correlation_strength
        self.missing_log: pd.DataFrame = self.mk_missing_log()

    def mk_missing_log(self) -> pd.DataFrame:
        ''' missing_log.loc[feat] = MAR(feat1, feat2) means "data from feat is missing-at-random with respect to feat1, feat2, ...

        pearson correlates are only calculated for features of zero nulls, right now.
        "'''

        def option_join(strings: Optional[List[str]],
                        withsep: str = ', ') -> Optional[str]:
            ''' if input is None propagate None, else join with withsep. '''
            if strings:
                return withsep.join(strings)
            else:
                return None

        def option_plus_paren(strings: Optional[List[str]],
                        withsep: str = ', ') -> Optional[str]:
            ''' if input is None propagate None, else concatenate and paren '''
            if strings:
                return 'MAR(' + withsep.join(strings) + ')'
            else:
                return None

        def strong_enough(corr_mat: pd.DataFrame, featu: str,
                          corr_strength: float = self.correlation_strength) -> Optional[List[str]]:
            ''' takes slice of a correlationmatrix and a strength parameter and returns a list of correlative features. '''
            xs = [k for k, v in (abs(corr_mat[featu]) >
                                 corr_strength).items() if v]
            if len(xs) > 1:
                return [x for x in xs if x != featu]
            else:
                return None

        cs: List[str] = [
            'missing_rate',
            'pearson_correlates',
            'missing_regime',
        ]

        observations: int = self.loader.df.shape[0]

        missing_log: pd.DataFrame = pd.DataFrame(
            columns=cs, index=self.loader.df.columns)

        missingness_corr: pd.DataFrame = self.loader.df.isna().astype(int).corr()

        correlation_matrix: pd.DataFrame = self.loader.df.corr()

        # None represents no correlates
        nan_correlates: Dict[str, Optional[List[str]]] = dict()
        # None represents no correlates.
        correlates: Dict[str, Optional[List[str]]] = dict()

        isnasum_rate: float = divide(
            self.loader.df.isna().sum(),
            self.loader.df.shape[0])

        for feature in tqdm(
                self.loader.df.columns,
                desc="counting nans, correlations, MAR-correlates..."):

            missing_log.missing_rate[feature] = isnasum_rate[feature]

            nan_correlates[feature] = strong_enough(missingness_corr, feature)

            if feature in correlation_matrix.columns:
                correlates[feature] = strong_enough(
                    correlation_matrix, feature)
                if correlates[feature]:
                    missing_log.pearson_correlates[feature] = option_join(
                        correlates[feature])

            if nan_correlates[feature]:
                missing_log.missing_regime[feature] = option_plus_paren(nan_correlates[feature])

        return missing_log

    def export_csv(self, name: Optional[str] = None, to_subdir: bool = True):
        ''' will automatically add '.csv' to filename

        to_subdir argument puts it in ../clean_dev, if False it puts it in .
        '''

        subdir: str = "playground"

        def mk_path(name: Optional[str], to_subdir: bool) -> Tuple[str, str]:
            path: str = '.csv'
            message: str = ''
            if name is not None:
                path = name + path
            else:
                path = self.loader.dump + '-MISSINGLOG' + path

            if to_subdir:
                message = " to " + subdir
                path = ''.join(['', subdir, '/', path])
            else:
                message = " here. "

            return (path, message)

        try:
            path, msg = mk_path(name, to_subdir)
            self.missing_log.to_csv(path_or_buf=path, index=False)
            sys.stdout.write("WROTE" + msg)
            sys.stdout.write('\r\b\r')

        except Exception as e:
            print(e)

        finally:
            pass
