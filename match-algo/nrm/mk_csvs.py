#!/usr/bin/env python

from itertools import product
from typing import Tuple, List, Dict, Any
from functools import reduce
from numpy.random import choice, randint
import pandas as pd

num_people: int = 150

num_projects: int = 25

len_prefs: int = 4 # how much preference data do you survey each person for?

names_people: List[str] = [a+b for a,b
                           in product("abcdefghijklmnopqrstuvwxyz",
                                      "abcdefghijklmnopqrstuvwxyz")
                            ][:num_people] # example names

names_projects: List[str] = [c for c
                             in "abcdefghijklmnopqrstuvwxyz"
                            ][:num_projects] # example projects

# every person gives a preference vector, we now randomly simulate the survey
preferences_ran: Dict[str, List[str]] = {person: list(choice(names_projects, len_prefs)) for person in names_people}
