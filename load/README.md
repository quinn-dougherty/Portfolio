# Data Loading Tool:

This is being used behind the scenes on the project [My
House](https://myhouse-pbi0bgqdc.now.sh/) at Lambda School, a home valuation
tool. 

Given a data dump in a number of csvs, iterate through them and apply cleaning
operations before concatenating them and writing them as one new, large csv-- all from
your terminal.

I wrote this tool so that even if the data dump updated twice a week through the
life of the project, the exploratory data analysis (EDA) and inference process
wouldn't have to be slowed down for my team to update on that data. 

```
13:05:20:load:$> python main.py -h
usage: main.py [-h] [--dumpname DUMPNAME] [--windows WINDOWS [WINDOWS ...]]
               [--filename FILENAME] [--writecsv WRITECSV]
               [--logmissing LOGMISSING]

Load a datadump of multiple uniform-column'd .csvs, run a couple cleaning and
filtering functions, and write and/or return a df.

optional arguments:
  -h, --help            show this help message and exit
  --dumpname DUMPNAME   the name dump you want to load.
  --windows WINDOWS [WINDOWS ...]
                        list of file signatures you want to load
  --filename FILENAME   name you would like for your output csv.
  --writecsv WRITECSV   would you like to write output csv? if not, set to
                        False. NOTE: currently not fully operational.
  --logmissing LOGMISSING
                        would you like to record info about missingness? if
                        not, set to False.
```

Through preliminary EDA on raw data, build up a list of features you know you want
to drop and place that list in `gvars.py`. You can do the same with columns you
know you want to keep. 

The values in `gvars.py` are the defaults of the command line arguments, but
they can be easily overridden as you see in the `usage`. 

It is fully [pep484](https://www.python.org/dev/peps/pep-0484/) compliant. 

## Bonus feature: missingness report

Too often, we take imputation for granted. At level one, we apply imputation
strategies _as if we're debugging_, i.e. we run `.fillna('mean')` because we just want it to let us train up for inference. At level two, we put a little more TLC into EDA and experimentation,
ending up with _motivated_ imputation strategies, i.e. thinking critically about the
interaction between imputation and other things in our pipeline, informed mostly by validation loss. 

In [this talk from SciPy 2018 by Dillon Niederhut](https://youtu.be/2gkw2T5jAfo) I found a proposal for
level three. The problem with level two is that we are 
erasing information with imputation-- namely, the distribution of missing vs.
nonmissing values. Without recalling that distribution, the reporting of results
can't be fully transparent. Niederhut calls for data
scientists to push publishing conventions in the direction of **reporting the
missingness at which you found the data** as a minimal requirement to interpret
results. 

So I knew I wanted to log missingness right away, in hopes that it would help
the team (myself included) make more informed decisions from the beginning, and
suggest imputation strategies to attempt. Even if it doesn't result in
information the consumer can use, it will help our team be more clever and more
honest internallly. The best way to do this is to have an auxiliary dataframe at
your fingertips to consult when you're iterating on a model or exploring feature
importances, coefficient sizes, etc.  

The three regimes of missingness are MCAR, MAR, and MNAR: 
- **MCAR: Missing Completely at Random**. Here, an imp is going around just
  deleting things at roll of the dice, just to get on your nerves. As Niederhut
  explains, there is a _very_ high burden of proof on believing that your data
  is MCAR. 
- **MAR: Missing at Random**. Here, you can show that any feature's missingness
  is correlated with missingness elsewhere in the data. This is the only one that was
  easy to script up, so it's the only regime I make hypotheses about
  automatically. 
- **MNAR: Missing Not at Random**. Here, information _within a feature** can
  explain the missingness of that feature. Showing exactly what that explanation
  is is quite a hard inference problem in itself even on a case by case basis,
  so i definitely didn't script it up in general. 
  
**All** imputation introduces bias, including just dropping rows. If you have an
_MCAR_ feature, filling with mean is a reasonable compromise (but the bargain is
that if you believe your feature is MCAR, it's probably wishful thinking). You
can show a feature is _MAR_ with respect to other features by a simple script
involving the correlation matrix of `df.isna().astype(int)` (which is what I did), and something like
`from fancyimpute import IterativeImputer` will be the most successful. If a
feature is _MNAR_, dropping is better than filling with mean. 

In all regimes, the **correlation matrix** not of the `.isna().astype(int)`
matrix but of the data itself can be a useful too, so I added a list of
correlates according to that matrix in the report as well. 

I hope that this tool can accelerate EDA on my team and increase honesty and
validation accuracy for our inference. 

Further resource: [`fancyimpute`](https://pypi.org/project/fancyimpute/)

And [a gentler introduction to the problem from scipy 2016](https://youtu.be/cHzahWjaA7o).

## highlight: yielding dataframes

One of the methods in my Load class takes the main share of heavy lifting-- it
makes the collection of dataframes that is to be consumed by `pd.concat`. If the
dumps get particularly large, this is the section of the program that will
stress a local machine. 

``` python
def df_iter_by_window(
        self, windows: List[str]) -> Iterator[pd.DataFrame]:
    ''' makes a dataframe from each file in data dump returns iterator'''
    for window in tqdm(windows, desc="cleaning & concatting..."):
        yield self.clean_(pd.read_csv(self.csv_path(window), low_memory=False))
```

I haven't stress tested it on large input yet, but my hypothesis is that _lazily_
building a collection of dataframes can be kinder on memory than ordinary list
comprehension. 

If you're unfamiliar with laziness in python or `yield`: [read Jeff Knupp's blog](https://jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/). Well, just in general read Jeff Knupp anyway. 

## highlight: `option_join` 
In the missingness report, I wanted to use python `None` at an intermediary stage to
represent "no correlations are strong enough", meaning that my function
`strong_enough` that takes a correlation matrix, a feature, and a strength
parameter to return a list of features that are strongly-enough correlated needs
to return `Optional[List[str]]`. A type **Optional[A]** passes a value that is
_either_ an `A` _or_ a `None`. 

When I ran `mypy`, I got a stern warning.

```
 Argument 1 to "join" of "str" has incompatible type "Optional[List[str]]"; expected "Iterable[str]"
```

Where `List` is a subtype of `Iterable`. What I need is for `', '.join(None)`.
to **propagate `None`** instead of `TypeError`.

``` python
def option_join(strings: Optional[List[str]],
                withsep: str = ', ') -> Optional[str]:
    ''' if input is None propagate None, else join with withsep. '''
    if strings:
        return withsep.join(strings)
    else:
        return strings
```

Since in the context of my program I'm passing this function after my
`strong_enough` function which is guaranteed by the semantics to return _either_
a nonempty list _or_ a `None`, the only "falsey" value that could possibly
appear after the `else:` is `None`.

_resource if the above is in klingon_: [Graham Hutton's intro to programming with
`Maybe`](https://youtu.be/t1e8gqXLbsU) (python `None` behaves a lot like haskell
`Nothing`)
