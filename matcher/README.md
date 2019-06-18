This is a proof-of-concept for a project that became
[Wizards](https://github.com/quinn-dougherty/wizards), which is currently
utilized at Lambda School. 

### Context: Capstone Projects at Lambda School

Lambda School has a rigorous capstone project program called Labs. The matching
problem is the following: Suppose two Lambda School students are Alice and Bob, and suppose that two
Lambda School projects are Pizza and Veggie Burgers. Alice prefers to be on the
Pizza project, and Bob prefers to be on the Veggie Burgers project, so we would
like both of them to be satisfied. Now scale it up to over a hundred people! 

In the following code
we have random toy data, where people are named `aa` and projects are named `A`,
where a is any lower case letter and A is any upper case letter.  

### My Solution

The repository you are reading was my proof of concept. TLDR, it's a version of
[stable marriage](https://en.wikipedia.org/wiki/Stable_marriage_problem) or the
[resident matching service](https://www.carms.ca/the-match/how-it-works/), with
a constraint that "projects" can't prefer "people", making the exactness of the
solution a hair weaker than that of my predecessors. 

The proof of concept can be read or cloned/ran [right here on
GitHub](https://github.com/quinn-dougherty/Portfolio/blob/master/matcher/matcher.py),
or you can read the production version which lives
[here](https://github.com/quinn-dougherty/wizards). Wizards, the production
version, differed first from the proof-of-concept when it factored the solver's
state into a database, and differed second when it automated the dropping of
unpopular projects to solve iteratively. Both the proof-of-concept and Wizards
are [verified by mypy](https://www.python.org/dev/peps/pep-0484/)

### Assumptions

Because we're interested in a group's satisfaction and effectiveness at a
project, no model or algorithm will capture all considerations, but a basic
**rank ordering** surveyed from each participant will be the level of
information we have about their preferences. 

This means we're ignoring conditionals like "If Bob is on Pizza then Alice
prefers Pizza, else Alice prefers Veggie Burgers", and in general suppressing
anything more detailed than **rank ordering**, so Bob's rank ordering might look
like `Veggie Burgers >> Pizza >> Third Project` where `>>` is [a kind of "greater
than" symbol](https://en.wikipedia.org/wiki/Preference_%28economics%29#Notation).

We will also, for this prototype, assume **every project has the same size
team** and assume **every person is surveyed for the same amount of preference
information**. 

# Model

We can track **People** and **Projects** by their names. 

A **Project** is equipped with a **team**, which is a **List of People**

A **Person** is equipped with their **preferences**. Since lists are *ordered*,
we can represent this as a **List of Projects**, because we can assume that `0th` index represents highest preference, and last index
represents lowest preference. A Person is also **assigned** to a project, and
being left "high and dry" so to speak is represented by `None`. Our code will
involve usage of `None` that is roughly at the level of [this computerphile
video](https://youtu.be/t1e8gqXLbsU). 

So let's draw up wrapper classes `Person` and `Project`. 

``` python

class Person(str): 
    def __init__(self, name: str): 
        self.name: str = name
        # Until the survey is conducted, preferences will be an empty string. 
        self.preferences: List[Project] = [] 
        # Because assigned is either a Project or a None, we wrap it in Optional.  
        self.assigned: Optional[Project] = None
        
    def __str__(self): 
        return self.name
    
    
class Project(str): 
    def __init__(self, proj_name: str, max_team: int = PEOPLE_PER_PROJECT): 
        self.proj_name: str= proj_name
        # Different projects can have a different number of team-members. 
        self.max_team: int = max_team
        
        self.team: List[Person] = []
        
    def __str__(self):
        return self.proj_name
```

## Satisfaction measure

I want to measure the total satisfaction of the group with a given assignment.
In other words, I want a function that takes an assignment, holds the rank
orderings of all the people constant, and returns a number. 

Since rank ordering is interpreted as list, and the `0th` item is
highest-preferred, **reverse index + 1** will give us a number. 

``` python
def satisfaction_(assigned_to: Project, preferences: List[Project]) -> int:
    ''' returns the satisfaction score of being assigned '''
    try: 
        # gain reverse index + 1 satisfaction from assignment
        return preferences[::-1].index(assigned_to) + 1
    except ValueError: 
        # gain zero satisfaction by getting assigned to a project you didn't list 
        return 0
```

To **normalize** satisfaction across all people, if they don't share a fixed
length of preferences, we have to divide it by the largest one

``` python
PREF_MAX: int = max([len(person.preferences) for person in PEOPLE])

def satisfaction(assigned_to: Project, 
                 preferences: List[Project], 
                 pref_max: int = PREF_MAX) -> float:
    '''returns normalized satisfaction'''
    return divide(satisfaction_(assigned_to, preferences), pref_max)
```

so an **assignment** is scored by **mean satisfaction**

``` python
def mean_satisfaction(people: List[Person]) -> float:
    ''' mean satisfaction of all participants '''
    assert len(people)>0, "ERROR: read in input list of people"
    return divide(sum([satisfaction(person.assigned, 
                                    person.preferences) 
                       for person 
                       in people]), 
                       len(people))
```


## Clone it! 

This is all set to run with toy data by command line, on any machine with a
basic scientific python build (for the poisson test). 

```
usage: main.py [-h] [--popularity-threshold POPULARITY_THRESHOLD]
               [--unpopularity-threshold UNPOPULARITY_THRESHOLD]
               [--poisson POISSON]

Solve the match with random preferences

optional arguments:
  -h, --help            show this help message and exit
  --popularity-threshold POPULARITY_THRESHOLD
                        how popular does a project have to be to be considered
                        for duplication?
  --unpopularity-threshold UNPOPULARITY_THRESHOLD
                        how many unpopular projects to print?
  --poisson POISSON     Use a poisson process to simulate unusually popular
                        projects?
```

