#!/usr/bin/env python

from argparse import ArgumentParser
from itertools import product
from typing import List
from matcher import Person, Project, PREF_MAX, unassigned_num, assign_to_nth, mean_satisfaction, popular, unpopular
from matcher import NUM_PROJECTS, NUM_PEOPLE, ALPHABET, PEOPLE, PROJECTS

parser = ArgumentParser(description='Solve the match with random preferences')
parser.add_argument('--popularity-threshold', type=int, default=3,
                    help='how popular does a project have to be to be considered for duplication? Default: surplus popularity > 4')
parser.add_argument('--unpopularity-threshold', type=int, default=4,
                    help='how many unpopular projects to print? Default: 4')
parser.add_argument('--poisson', type=bool, default=False,
                    help="Use a poisson process to simulate unusually popular projects? Default: False")
parser.add_argument('--reset', type=bool, default=True, help='reset assignments? Default: True')

args = parser.parse_args()
RESET = bool(args.reset)

def solve(people: List[Person],
          projects: List[Project],
          iters: int = PREF_MAX,
          report: bool = True,
          poisson_bool: bool = False):
    ''' solves. Prints stepwise report if bool=True.
    prints final report either way.  '''

    for k in range(iters): 
        if report: 
            print(f"{unassigned_num(people)} are still unassigned. ")
        # solve
        assign_to_nth(people, k, poisson_bool=bool(poisson_bool))

    print(f"Match finished. {unassigned_num(people)} are left unmatched. ")

    popularity_report = ', '.join(str(x)
                                  for x
                                  in popular(projects,
                                             threshold=args.popularity_threshold))

    unpopularity_report = ', '.join(str(x)
                                    for x
                                    in unpopular(projects,
                                                 threshold=args.unpopularity_threshold))

    print()
    
    popularity_tuples = popular(projects, threshold=args.popularity_threshold)
    if not popularity_report: 
        print(f"No projects have more than {args.popularity_threshold} surplus popularity. ")
    else: 
        print("\n".join(f"Project {t[0]} has {t[1]} surplus popularity" for t in popularity_tuples))
    print()

    unpopularity_tuples = unpopular(projects, threshold=args.unpopularity_threshold)
    if not unpopularity_report: 
        print(f"No projects have less than {args.unpopularity_threshold} people. ")
    else: 
        print("\n".join(f"Project {t[0]} as {t[1]} people assigned to it. " for t in unpopularity_tuples))

    print()
    tot_sat = mean_satisfaction(people)
    print(f"The mean satisfaction of this match is {tot_sat}. ")
    pass


if __name__ == '__main__':

    solve(PEOPLE, PROJECTS, poisson_bool=bool(args.poisson))
