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
like `Veggie Burgers >> Pizza >> Third Project` where `>>` is (a kind of "greater
than" symbol)[https://en.wikipedia.org/wiki/Preference_%28economics%29#Notation].

## This post

I wanted to talk about my process, document the rabbit holes I went down, and make
a meta-comment about not being sniped by the *wrong* rabbit holes. 

Please skip only to the parts you're interested in, or read all the way through!

[Basic Model](#Model): Assumes some basic Python, literacy in type
signatures or `pep484`, and advanced usage of `None`.
[Combinatorics?](#Combinatorics?): Very formal, assumes literacy in discrete mathematics.
[Interpretation: Utility Maximization](#Interpretation: Utility Maximization):
Explains how to interpret this as an optimization problem. 
[Solution: Optimization and Search?](#Solution: Optimization and Search?): Some sketches and discussion
of search methods. 
[Solution: The Roth-Peranson Resident Matching Algorithm?](#Solution: For Medical School?): A
problem similar to this is assigning med students to med schools, and an
excellent solution is known. Will it work for us? 
[My Solution, with caveats](#My Solution, with caveats): 

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
    def __init__(self, proj_name: str, max_staff: int = PEOPLE_PER_PROJECT): 
        self.proj_name: str= proj_name
        # Different projects can have a different number of team-members. 
        self.max_team: int = max_staff
        
        self.team: List[Person] = []
        
    def __str__(self):
        return self.proj_name
```

# Combinatorics? 

# Interpretation: Utility Maximization

# Raw Search Power? 

# For Medical School?

# My Solution


# assign `N` things into `K` bins, presumably each bin can support `N/K` things. 

Survey each thing for the bin it'd prefer, limited to rank ordering. 
Interpret _utility_ of being assigned to a bin as the index of that bin appearing in the reversed preference list of each thing. 

# optimization problem-- find the assignment that maximizes `self.total_utility()`. 

I'm 98% it's exponential in num projects, a rough upper bound is ~$\binom{n}{n//k} ^{k}$ where n is number of people and k is number of projects (and, i.e. python, n//k is floor divide). I *don't* expect brute force `argmax` to be viable. 

# solutions proposed
Something like [simulated annealing](https://en.wikipedia.org/wiki/Simulated_annealing) could work ok. Our friend also sketched what an evolutionary solution would look like. 

[This solution](https://github.com/J-DM/Roth-Peranson) could be adapted, few differences. This was actually an issue among med schools and someone got a nobel for solving it.  

_The following were notes, stream of consciousness
# one way to approach optimization is derivatives, but what's *derivative of utility with respect to assignment*, holding preferences constant? 

An assignment `Dict[project, List[person]]`, and with the constraint that **every person is in exactly one project** it is in fact _invertible_. But every invertible map from A to collections of B is also a non-injective map from B to A, so we could in fact rewrite `assignment` as `Dict[person, project]`. 

what is a derivative? it is when the observer _wiggles_ input to see what it does to output. our input type is a set of non-injective maps. 


## How do we wiggle a set of non-injective maps? 
i'm _guessing_ something to do with [finite differences](https://en.wikipedia.org/wiki/Finite_difference#difference_operator). 

We know we can _rearrange_ the mapping. Maybe a mapping containing both `alice->pizza, bob->tofu` is "one step away" from a mapping that's exactly the same except `alice->tofu, bob->pizza`. But will that help us with the _numeric_ side, the value/utility of a mapping?


