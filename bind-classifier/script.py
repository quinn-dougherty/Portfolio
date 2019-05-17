from __future__ import division
import pickle


import itertools
import numbers
import numpy as np# type: ignore
from warnings import warn
from abc import ABCMeta, abstractmethod

from sklearn.base import ClassifierMixin, RegressorMixin # type: ignore
from sklearn.externals.joblib import Parallel, delayed# type: ignore
from sklearn.externals.six import with_metaclass# type: ignore
from sklearn.externals.six.moves import zip# type: ignore
from sklearn.metrics import r2_score, accuracy_score# type: ignore
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor# type: ignore
from sklearn.utils import check_random_state, check_X_y, check_array, column_or_1d# type: ignore
from sklearn.utils.random import sample_without_replacement# type: ignore
from sklearn.utils.validation import has_fit_parameter, check_is_fitted# type: ignore
from sklearn.utils import indices_to_mask, check_consistent_length# type: ignore
from sklearn.utils.metaestimators import if_delegate_has_method# type: ignore
from sklearn.utils.multiclass import check_classification_targets# type: ignore

from sklearn.ensemble.base import BaseEnsemble, _partition_estimators# type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer

with open('estimators_tup.pickle', "rb") as p:
    seq_tfidf, lig_tfidf, bc = pickle.load(p)

with open('dfs.pickle', "rb") as d:
    ligs, seqs, binds = pickle.load(d)

def predict(ligid: str, seqid: str) -> float:
    one = seqid in binds[binds.lig==ligid].seq.values and ligid in binds[binds.seq==seqid].lig.values
    if one: 
        return 1
    else: 
        x = seq_tfidf.transform([seqs.iloc[ligid].sequence]).toarray()[0]
        y = lig_tfidf.transform([ligs.iloc[seqid].SMILES]).toarray()[0]
        xx = [list(x) + list(y)]
        return bc.predict_proba(xx)[0][0]

#print(predict(ligid, seqid))
#sys.stdout.flush()

