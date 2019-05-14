''' vars like lists of features should be here. '''
from typing import List

DUMP: str = 'dump' # directory name

FILE_SIGNATURES: List[str] = [
    '0', '1',  ] # list of unique filenames.

# list of columns to drop
TO_DROP: List[str] = ['List', 'of', 'columns', 'to', 'drop']

# alternatively, you can pick out columns to keep
TO_KEEP: List[str] = ['columns', 'to', 'keep'
           ]

# inference target column name
TARGET: str = 'y'
