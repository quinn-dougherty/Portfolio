from itertools import product
from typing import Tuple, List, Dict, Any
from functools import reduce
from numpy.random import choice, randint

num_people = 150

num_projects = 25

len_prefs = 4 # how much preference data do you survey each person for?

names_people = [a+b for a,b in product("abcdefghijklmnopqrstuvwxyz", 
                                       "abcdefghijklmnopqrstuvwxyz")
               ][:num_people] # example names

names_projects = [c for c 
                  in "abcdefghijklmnopqrstuvwxyz"
                 ][:num_projects] # example projects

# every person gives a preference vector, we now randomly simulate the survey
preferences_ran = {person: list(choice(names_projects, len_prefs)) for person in names_people}


# assigning a person to a project they stronger preferred gives more utility than assigning them to a project they weaker prefer

def _rv_getidx_orzero(x: Any, xs: List[Any]) -> int: 
  '''idx of first occurence, 0 if not in
  '''
  if x not in xs: 
    return 0
  else: 
    for k,v in enumerate(xs[::-1]): 
      if x==v: 
        return k 

class assignment: 
  '''This object assumes we have survey data in outer state, but randomized survey data for example'''
  def __init__(self, people: List[str], projects: List[str]): 
    self.people = people
    self.projects = projects
    self.preferences_ran = {person: list(choice(self.projects, len_prefs)) 
                            for person in self.people} # survey data
    self.preferences_ran_const = preferences_ran
    
    # assumption: every project has the same number of people
    self.random_assignment = {project: [people.pop(randint(1, len(people)) - 1)
                                        for _ in range(num_people//num_projects - 1)]
                              for project in self.projects}

  def total_utility(self, preferences: Dict[str, List[str]] = None) -> int: 
    '''interpret index of a person's reversed preference vector +1 as the 
        utility of getting assigned to that project, so;
    
    U(project at preference index 0) == len_prefs
    U(project at preference index 1) == len_prefs-1
    ...
    U(project at preference index len_prefs-1) == 1
    '''
    
    assignment = self.random_assignment
    preferences = self.preferences_ran
    if assignment==self.random_assignment or preferences==self.preferences_ran: 
      print("running on RANDOMIZED EXAMPLE data ")
    
    
    return sum([sum([sum([_rv_getidx_orzero(project, preferences[person]) 
                          for project in preferences[person]]) 
                     for person in assignment[project_]])
                for project_ in assignment.keys()])

U = assignment(names_people, names_projects).total_utility()

