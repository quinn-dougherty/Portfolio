# usage: 

Right now you have to manually download and unzip the dump from gdrive. 

**also ensure that each filename in `04-24` dir is in `ddd-ddd` format!**

The goal is that when we get larger dumps, we assume the schema of features is the same, and we can trivially put it back into our pipeline. 

```
cd ds-scripts/load
python main.py
``` 

```
$> python main.py -h
usage: main.py [-h] [--dumpdate DUMPDATE]
                    [--windows WINDOWS [WINDOWS ...]] [--filename FILENAME]
                    [--writecsv WRITECSV] [--logmissing LOGMISSING]

Load a datadump of multiple uniform-column'd .csvs, run a couple cleaning and
filtering functions, and write and/or return a df.

optional arguments:
  -h, --help            show this help message and exit
  --dumpdate DUMPDATE   the date of the dump you want to load in mm-dd format.
  --windows WINDOWS [WINDOWS ...]
                        list of windows you want to load in ddd-ddd format,
                        where number of days is measured in ddd minus date of
                        export (see mm-dd/README.md for more details)
  --filename FILENAME   name you would like for your output csv.
  --writecsv WRITECSV   would you like to write output csv? if not, set to
                        False. (note, currently bugged)
  --logmissing LOGMISSING
                        would you like to record info about missingness? if
                        not ,set to False.
```

**NOTE: defaults to values in `gvars.py` if you give it no arguments.** 

**note; I haven't gotten `--writecsv=False` to work for some reason.**


## The next step would be automatically pulling it down from gdrive (or perhaps better an s3 bucket), but we can build on this for that.


### a program taking raw datadump and producing a more useful csv

- it also writes a missingness csv, to log information abbout missingness. A stretch goal is for this to infer the correct imputation strategy, but in it's current form it can recommend strategies to you indirectly. 

- basic glossary about missingness is: 
- - `MAR` is "missing at random", this is the main target, it has to do with _correlation to other features_. This is where you can look at _other_ features to predict missingness of _this_ feature. I've _already_ written code to automagically infer this, to an extent.  
- - MCAR is "missing completely at random", this is where a demon is removing rows by flipping a truly random coin. (this is the only situation where it's _remotely_ permissible to fillna(df.feat.mean()), and most of the time when you think you have MCAR it's wishful thinking. inevitably, we're going to fall back on this when we don't have other options. I _very likely will not_ be able to write good inference to automage this.  
- - MNAR is "missing not at random", where you can predict the pattern of when a feature is missing _by looking directly at the feature_. I believe I will **not** be able to infer this _in general_, it needs human EDA or domain expertise, feature-by-feature.  

so if you look at the `MISSINGLOG` csv, the rows `feat` that have `MAR(feat1, feat2, ...)` are saying "we believe that `feat1`, `feat2`, `...` are missing for the same reasons `feat` are missing. "



