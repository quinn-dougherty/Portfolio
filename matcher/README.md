# The problem: 

The problem is **assignment*. In particular, match 150 people into 25 projects. 

### Context: capstone projects at Lambda School

So, suppose two Lambda School students are Alice and Bob, and suppose that two
Lambda School projects are Pizza and Veggie Burgers. 

### My solution

I spent a lot of time approaching this from a lot of angles, and found a
solution that, in hindsight, is very simple. 

### Assumptions

Because we're interested in a group's satisfaction and effectiveness at a
project, no model or algorithm could capture all considerations, but a basic
**rank ordering** surveyed from each participant will be the level of
information we have about their preferences. 

This means we're ignoring conditionals like "If Bob is on Pizza then Alice
prefers Pizza, else Alice prefers Veggie Burgers", and in general suppressing
anything more detailed than **rank ordering**, so Bob's rank ordering might look
like `Veggie Burgers >> Pizza >> Third Project` where `>>` is [a kind of "greater
than" symbol](https://en.wikipedia.org/wiki/Preference_%28economics%29#Notation).

## This post

I wanted to talk about my process, document the rabbit holes I went down, and make
a meta-comment about not being sniped by the *wrong* rabbit holes. 

Please skip only to the parts you're interested in, or read all the way through!

- [Basic Model](#Model): Assumes some basic Python, literacy in type
signatures or `pep484`, and advanced usage of `None`.
- [Interpretation: Utility Maximization](#Interpretation:-Utility-Maximization):
- [Combinatorics?](#Combinatorics?): Very formal, assumes literacy in discrete mathematics.
Explains how to interpret this as an optimization problem. 
- [Solution: Optimization and Search?](#Solution:-Optimization-and-Search?): Some sketches and discussion
of search methods. 
- [Solution: The Roth-Peranson Resident Matching Algorithm?](#Solution: For
Medical School?): A
problem similar to this is assigning med students to med schools, and an
excellent solution is known. Will it work for us? 
- [My Solution, with caveats](#My-Solution, with caveats): 

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

# Interpretation: Utility Maximization

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

# Combinatorics? 

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

# Raw Search Power? 

No. 

The number of possible assignments is [`NUM_PROJECTS ** NUM_PEOPLE -
sum([binom(NUM_PROJECTS, k) * (NUM_PROJECTS-k)**NUM_PEOPLE for k in range(1,
NUM_PROJECTS)])`](https://mathoverflow.net/questions/29490/how-many-surjections-are-there-from-a-set-of-size-n).
At `150` people and `25` projects, it's number with `206` decimal places according to
Python. I'm assuming I can't run that. 

Many search techniques are way better than exhaustive, but don't guarantee
convergence, and offer no way of knowing whether is a local optima or the global
one. I decided they wouldn't be satisfying enough to be worth the trouble, even
though it would have been good practice for me to implement them. 

And a note, gradient descent doesn't fit our criteria for an **awesome** solver,
even though it'd be quite good. 

# For Medical School? <a name="#Solution: For Medical School?"></a> 

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

>! Nothing. All people return unassigned. 

So, adapting the *exact* med school algorithm doesn't work. 

# My Solution

