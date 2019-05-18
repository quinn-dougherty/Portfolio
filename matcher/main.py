#!/usr/bin/env python

from typing import List
from matcher import *
from argparse import ArgumentParser

parser = ArgumentParser(description='Solve the match with random preferences')
parser.add_argument('--popularity-threshold', type=int, default=4,
                    help='how popular does a project have to be to be considered for duplication?')
parser.add_argument('--unpopularity-threshold', type=int, default=4,
                    help='how many unpopular projects to print?')
parser.add_argument('--poisson', type=bool, default=False,
                    help="Use a poisson process to simulate unusually popular projects?")

args = parser.parse_args()


def solve(people: List[Person] = PEOPLE,
          iters: int = PREF_MAX,
          report: bool = True,
          poisson: bool = False):
    ''' solves. Prints stepwise report if bool=True.
    prints final report either way.  '''
    if report:
        for k in range(iters):
            unassigned = unassigned_num(people)
            print(f"{unassigned} are still unassigned..")
            assign_to_nth(PEOPLE, k)

    else:
        for k in range(iters):
            assign_to_nth(PEOPLE, k, poisson=poisson)

    print(f"Match finished. {unassigned} are currently unmatched. ")

    popularity_report = ', '.join(str(x)
                                  for x
                                  in popular(PROJECTS,
                                             threshold=args.popularity_threshold))

    unpopularity_report = ', '.join(str(x)
                                    for x
                                    in unpopular(PROJECTS,
                                                 threshold=args.unpopularity_threshold))

    print()
    print("In the following, the tuple (project, int) represents a project annotated by how many times someone was rejected from it. ")
    print(f"The projects {popularity_report} are very popular. ")
    print()

    print("In the following, the tuple (project, int) represents a project annotated by how many people are in it. ")
    print(f"The projects {unpopularity_report} are rather unpopular")

    print()
    tot_sat = mean_satisfaction(PEOPLE)
    print(f"The mean satisfaction of this match is {tot_sat}. ")
    pass


if __name__ == '__main__':
    from matcher import *
    solve(PEOPLE, poisson=args.poisson)
