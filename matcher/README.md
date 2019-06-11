# The problem: 

The problem is *assignment*. In particular, match 150 people into 25 projects. 

### Context: Capstone Projects at Lambda School

Suppose two Lambda School students are Alice and Bob, and suppose that two
Lambda School projects are Pizza and Veggie Burgers. But in the following code
we have random toy data, where people are named `aa` and projects are named `A`,
where a is any lower case letter and A is any upper case letter.  

### My Solution

I spent a lot of time approaching this from a lot of angles, and found a
solution that, in hindsight, is very simple. With some caveats, it can be
guaranteed to converge, and in the worst case randomness only impacts `<10%` of
people.
You can [read the code here on GitHub!](https://github.com/quinn-dougherty/Portfolio/blob/master/matcher/matcher.py)

It's similar to the [stable marriage problem](https://en.wikipedia.org/wiki/Stable_marriage_problem), but differs in that the provision of rank-ordering is one-sided. 

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

## This Post

I wanted to talk about my process and document the rabbit holes I went down
before presencting a pretty-good solution. 

Please skip only to the parts you're interested in, or read all the way through!

- [Basic Model](#Model): Assumes some basic Python, literacy in type
signatures or `pep484`, and advanced usage of `None`.
- [Interpretation: Utility Maximization](#utility):
- [Combinatorics?](#combinatorics): Very formal, assumes literacy in discrete mathematics.
Explains how to interpret this as an optimization problem. 
- [Solution: Brute Force?](#search): Some sketches and discussion
of search methods. 
- [Solution: The Roth-Peranson Resident Matching Algorithm?](#medschool): A
problem similar to this is assigning med students to med schools, and an
excellent solution is known. Will it work for us? 
- [My Solution, with caveats](#finale): 

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

If you're just here for the Python, it's time to [skip to the end](#finale)

# Interpretation: Utility Maximization <a name="utility"></a>

Now that we have a _number_ we can interpret the quest for the best assignment
as the **maximization of a function**. We know that some assignments will have
lower scores, and that other assignments will have higher scores. 

There are two basic kinds of solutions to problems of this type. One solves with
determinism, you input conditions and it outputs the solution. These are called
*analytic*. The other is an approximation, often with an element of randomness.
These are called *numeric*. 

We want a solution that at least improves upon the current process for matching
people to projects, but it would be **awesome** to have a solution that spits
out a provable global maximum rather than a local one or a "seems legit"
solution that is at least better than any known alternatives. 

Solutions to optimization problems have **convergence guarantees** and
**randomness independence** in either strong or weak amounts. So a solver that
only even works 5% of the time and is very nondeterministic would have weak
convergence guarantees and weak randomness independence, and an algorithm that
almost always converges and is almost the same every time has strong convergence
guarantees and strong randomness independence. 

In addition to a proof that the output is globally optimal, an **awesome**
solution should have strong convergence guarantees and enough determinism that
everyone agrees the outcome is fair. 

Does an **awesome** solution exist? 

# Combinatorics? <a name="combinatorics"></a> 

If an **awesome** solution exists, one of the first steps you can take toward
finding it is understanding the function space. Sometimes, the _size_ of a
function space shows you important information about it. 

One of the most straightforward ways to optimize something is to understand it's
**derivative**. A **derivative** is a measure of *change* of output upon a
specified amount of *wiggling* of input. This is obvious for our `y=x^2` sort of
functions, because taking `x` plus and minus infinitessimal amounts suffices for
our meaning of "wiggling". **Gradient descent** is an optimization technique
roughly in the *numerical* family, that consists of repeatedly stepping in the
direction where change is greatest, as measured by derivatives. 

Could we format a derivative here? No. I don't know enough math. But I'd like to
take you on the journey toward realizing this, because it illustrates what the
complexity of an exact, **awesome** solution might be.

Let's think of our function as the type `Assignment -> float`, for some
assignment type. Our problem comes with the constraint that every project is
assigned to only one team, so an assignment could be a map `Projects ->
List[Person]`, which in Python's notation is simply `Dict[Projects, List[Person]]`. If we think of project teams as subsets of people, and we
notice that project teams are non-overlapping, then we can think of this
codomain as a collection of subsets. While assignments are bijective, we can
interchange domain for codomain and remove the subset-ing of `Person`, making
assignments the *surjections* `Person -> Project` or `Dict[Person, Project]`.
Recall that whenever `len(d.keys()) > len(d.values())`, maps `d` necessarily
violate injectivity (`{'k': 0, 'l': 0}` is a perfectly good dictionary, but it
is not injective). 

Ok, so `satisfaction : (Person -> Project) -> float` is a reasonable type, but
can I take derivatives of its elements? To ask is to ask the following: can I
*wiggle* the surjections `Person -> Project`. 

And the answer is yes. Because I can knight the surjections `Person -> Project`
into the royal order of **permutation groups**, where the action of switching a
person to a different project is interpreted as our *unit of change*, in other
words, we found the wiggle... sort of. Since I don't have *infinitessimal*
wiggling, I don't know exactly how to take a derivative. I know how to [hack
together something like gradient descent on `Nat`](https://en.wikipedia.org/wiki/Finite_difference#difference_operator), which doesn't have
infinitessimal wiggling either, but I don't know how to do it on permutation
groups. Gradient descent on permutation groups seems like the kind of thing you
read about on the [John Baez](https://twitter.com/johncarlosbaez) cluster of twitter, whatever it is it's probably got
a big "don't try this at home" label on it. 

# Raw Search Power? <a name="search"></a>

No. 

The number of possible assignments is [`NUM_PROJECTS ** NUM_PEOPLE -
sum([binom(NUM_PROJECTS, k) * (NUM_PROJECTS-k)**NUM_PEOPLE for k in range(1,
NUM_PROJECTS)])`](https://mathoverflow.net/questions/29490/how-many-surjections-are-there-from-a-set-of-size-n).
At `150` people and `25` projects, it's number with `209` decimal places according to
Python. I'm assuming I can't run that. 

Many search techniques are way better than exhaustive, but don't guarantee
convergence, and offer no way of knowing whether is a local optima or the global
one. I decided they wouldn't be satisfying enough to be worth the trouble, even
though it would have been good practice for me to implement them. 

And a note, gradient descent doesn't fit our criteria for an **awesome** solver,
even though it'd be quite good. 

# Medical School? <a name="medschool"></a> 

We're stepping back to the real world. Math is fun but it's not _practical_.
Sometimes you just need to *get it done*. 

It had turned out that med schools were dealing with a similar problem.
Applicants to residence programs would report rank ordered lists of schools, and
schools would report rank ordered lists of applicants. But it wasn't understood
until recently, when Nobel-winning work on _stable allocation_ was adapted into
a solution that's now in use in several countries' residency programs. This
[splainer from Canada](https://www.carms.ca/the-match/how-it-works/) provides a nice
pseudocode of the process. 

It looks like the ability for schools to, in turn, prefer applicants divides out
some complexity for them and strengthens it's convergence guarantee and
determinism. We don't have that, our projects can't prefer people. 

I found a [Python implementation nicely set up on github by John Dirk
Morrison](https://github.com/J-DM/Roth-Peranson), and briefly adapted it to our
use case. 

If you'd like, spend some time trying to predict what will happen if "projects"
are each given the empty rank ordering.

> Nothing. All people return unassigned. 

So, adapting the *exact* med school algorithm doesn't work. 

# My Solution <a name="finale"></a>

I don't have a lot of experience with this sort of thing, but after some
exploration I have decided that **my solution will not be awesome**. 

That's when it hit me. _Weaken_ the convergence guarantees, _let in_ a little
nondeterminism, and then, of course, you know, you just 

``` python
for k in range(PREF_MAX):
    assign_to_nth(PEOPLE, k)
```

Assuming you know how to go through a list and just assign people to their `nth` preference.

``` python
def assign_to_nth(people: List[Person], n: int):
    ''' Assign a person to their nth preference.
    '''
    for pers in get_unassigned(people):
        if not pers.assigned:
            nth = pers.preferences[n]
            nth.add_person(pers)
```

Assuming you wrote the helper function `get_unassigned`

``` python
def get_unassigned(people: List[Person]) -> List[Person]:
    ''' Take a list of people and return the sublist of those who are not
    assigned yet. '''
    return [pers for pers in people if not pers.assigned]
```

And, finally, assuming you added the `add_person` method to the `Project` class. The `add_person`
method is the most crucial part, because it leaves the value `person.assigned` at
`None` if that particular project is already full

``` python
    # in Project class
    ... 
    def add_person(self, name: Person):
        if len(self.team) <= self.max_team_size:
            self.team.append(name)
            name.assigned = self
        else:
            self.popular += 1
    ...
```

This algorithm will certainly do _something_, I wonder how many people it leaves high and
dry? 

Here is the complete initialization procedure for the following outcome: 
- `NUM_PEOPLE = 150`
- `NUM_PROJECTS = 25`
- `TEAM_SIZE = NUM_PEOPLE//NUM_PROJECTS` Note, this is actually more stringent
  than the real life use case, in which this number is a variable and the sum of
  all the team sizes is slightly hgiher than `NUM_PEOPLE//NUM_PROJECTS`.
- `LEN_PREFS = 5` This algorithm supports rank orderings of arbitrary length.
  Here, we'll fix to a constant. 
  
Adding a report to show us how many people are left unmatched after each pass
through the `for` loop, we get this: 

``` python-console
150 are still unassigned..
10 are still unassigned..
4 are still unassigned..
2 are still unassigned..
0 are still unassigned..
Match finished. 0 are currently unmatched. 
```

The mean satisfaction of this match is `~0.9`. That's roughly consistent with
the observation that `150 - 10 - 4 - 2` people made it into their first choice, but I
won't show the weighted sum here. 

This run converged. It looks like the probability of convergence is, holding
`NUM_PEOPLE` and `NUM_PROJECTS` constant, a function of `TEAM_SIZE` and
`LEN_PREFS`. If the rank order lists were each length 3, two people would have
been left high and dry (completely unassigned). 

While the outcome is dependent on randomness-- the order in which the list of
people is consumed -- only 16 people are even effected by that, since only 16
people didn't get into their first choice. 

I'm sure when it's implemented for the next round of capstone projects at Lambda
next week it won't run _quite_ this smooth, because there are other
considerations that need to be considered and implemented. But for a decidedly
not **awesome** solution, this is pretty grand. 

## What if the distribution of project popularity is out of wack? 

One more thing we should test out is if one or two projects are unusually
popular. 

We can model this by generating the toydata's preferences with a
[poisson](https://en.wikipedia.org/wiki/Poisson_distribution) random variable
from `scipy.special`.  

``` python
# in the Person class, 
...
     self.preferences_poisson: List[Project] = [PROJECTS[clip(poisson.rvs(mu=9), 
                                                              0, 
                                                              NUM_PROJECTS-1)] 
                                               for _ 
                                               in range(LEN_PREFS)]
...
```

This will mean that the project that happens to lie in the neighborhood of the index, and
it's neighbors, will be too popular and will have to reject people more often. 

Let's see what happens when we run this. 

``` python-console
150 are still unassigned..
17 are still unassigned..
7 are still unassigned..
2 are still unassigned..
2 are still unassigned..
Match finished. 2 are currently unmatched. 

Surplus popularity of project C: 11

Understaffed: Project J at 2 team members.

The mean satisfaction of this match is 0.8906666666666666. 
```

_Even in this case_ it performs quite well, because the length of the survey is
long **relative** to the max team size.

**Remember: The shorter the survey, the weaker the results!**.
 
In a measure of a project's _surplus popularity_, `self.popularity += 1` every time
the `Project.add_person` method rejects someone, I found that 11 people who
wanted project C most couldn't fit into it. That's a lot-- more than enough to
justify duplicating the project, (by the same token, we can measure if groups
end up too small-- at around two people, and those would be candidates to be
dropped). Every time the program runs, management can make decisions like those,
adjust the initial conditions to implement them, and run it again. This process
can be iterated until the convergence is as close as desired.

All things considered, mean satisfaction is still pretty good. 

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

