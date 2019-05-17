#!/usr/bin/env python

import pandas as pd

from RothPeranson import MatchController

if __name__=='__main__':
    project_names_as_columns = pd.read_csv('project_names_as_columns.csv')
    student_preferences = pd.read_csv('student_preferences.csv')

    test_match = MatchController(project_names_as_columns, student_preferences)

    test_match.start_match()
    results = test_match.results_dict()

    print(results)
