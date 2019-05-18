#!/usr/bin/env python
''' Matching algorithm, similar to Roth-Peranson's resident matching services but a slightly different usecase. '''
from random import choice
from typing import Optional, List, Tuple
from itertools import product
from math import isclose
from numpy import divide, clip
from scipy.stats import poisson

# global vars
NUM_PEOPLE: int = 150
NUM_PROJECTS: int = 25
LEN_PREFS: int = 3
PEOPLE_PER_PROJECT: int = NUM_PEOPLE//NUM_PROJECTS
ALPHABET: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# two wrapper classes
class Person(str):
    def __init__(self, name: str):
        ''' currently initializing to random preferences '''
        self.name: str = name

        # to simulate unusually popular projects
        self.preferences_poisson: List[Project] = [PROJECTS[clip(poisson.rvs(mu=9), 0, NUM_PROJECTS-1)] for _ in range(LEN_PREFS)]

        # regular randomness
        self.preferences: List[Project] = [choice(PROJECTS) for _ in range(LEN_PREFS)]

        # project person is assigned to.
        self.assigned: Optional[Project] = None

    def __str__(self):
        return self.name

class Project(str):
    def __init__(self, proj_name: str, max_team_size: int = PEOPLE_PER_PROJECT):
        self.proj_name: str= proj_name
        self.max_team_size: int = max_team_size
        self.team: List[Person] = list()
        self.popular: int = 0

    def __str__(self):
        return self.proj_name

    def add_person(self, name: Person):
        if len(self.team) <= self.max_team_size:
            self.team.append(name)
            name.assigned = self
        else:
            self.popular += 1
            return None #print("CANT FIT ", name, " into this project!")


### **** MORE GLOBAL VARS ****
PROJECTS: List[Project] = [Project(x) for x in ALPHABET][:NUM_PROJECTS]

PEOPLE: List[Person] = [Person(f"{x[0]}{x[1]}")
                        for x
                        in product(ALPHABET.lower(), ALPHABET.lower())][:NUM_PEOPLE]

PREF_MAX: int = max([len(person.preferences) for person in PEOPLE])

MAX_TEAM: int = max([project.max_team_size for project in PROJECTS])

### **** SOLVER *****
def get_unassigned(people: List[Person]) -> List[Person]:
    return [pers for pers in people if not pers.assigned]

def assign_to_nth(people: List[Person],
                  n: int,
                  poisson: bool = False):
    ''' Assign a person to their nth preference.

    poisson will generate random preferences with a poisson process, to simulate
    '''
    for pers in get_unassigned(people):
        if poisson:
            if not pers.assigned:
                nth = pers.preferences_poisson[n]
                nth.add_person(pers)
        else:
            if not pers.assigned:
                nth = pers.preferences[n]
                nth.add_person(pers)


#################################################################################
###
### * * * * * * * * SATISFACTION / UTILITY INTERPRETATION * * * * * * *
###
#################################################################################

def satisfaction_(assigned_to: Project, preferences: List[Project]) -> int:
    ''' returns the satisfaction score of being assigned '''
    try:
        # gain reverse index + 1 satisfaction from assignment
        return preferences[::-1].index(assigned_to) + 1
    except ValueError:
        # gain zero satisfaction by getting assigned to a project you didn't list
        return 0

def satisfaction(assigned_to: Project,
                 preferences: List[Project],
                 pref_max: int = PREF_MAX) -> float:
    '''returns normalized satisfaction'''
    return divide(satisfaction_(assigned_to, preferences), pref_max)

def mean_satisfaction(people: List[Person]) -> float:
    ''' mean satisfaction of all participants '''
    assert len(people)>0, "ERROR: read in input list of people"
    return divide(sum([satisfaction(person.assigned,
                                    person.preferences)
                       for person
                       in people]),
                       len(people))

########################################################################
###
### * * * * * * * UTILS FOR REPORTING
###
########################################################################

def unassigned_num(people: List[Person]) -> int:
    ''' get the number of unassigned people. '''
    return len(get_unassigned(people))

def popular(projects: List[Project], threshold: int = 0) -> List[Project]:
    ''' sort projects by the popularity incrementer '''
    return sorted([(project, project.popular) for project in projects if project.popular > 0],
                   reverse=True,
                   key = lambda project_tup: project_tup[0].popular)

def unpopular(projects: List[Project], threshold: int = 3) -> List[Project]:
    ''' show projects with the lowest amount of people '''
    return sorted([(project, len(project.team)) for project in projects],
                   reverse=False,
                   key = lambda project_tup: len(project_tup[0].team))[:threshold]

###############################
### * * * * UNIT TEST * * * * *
###############################
assert isclose(mean_satisfaction(PEOPLE), 0)
