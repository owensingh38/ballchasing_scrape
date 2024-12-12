# Ballchasing_Scrape

Ballchasing_Scrape is a Python package for scraping information and stats from Rocket League replays hosted on ballchasing.com.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Ballchasing_Scrape.

```bash
pip install ballchasing_scrape
```

## Usage
Sample script collecting replays from the RLCS 2024 World Championship and exporting them into a single folder.

```python
import pandas as pd
import ballchasing_scrape as bc
import os

#Stats import
groups = [
    'https://ballchasing.com/group/fur-vs-ssg-6p2jrte6kd',
    'https://ballchasing.com/group/m8-vs-oxg-209d7inbro',
    'https://ballchasing.com/group/flcn-vs-kc-5capn4b1aq',
    'https://ballchasing.com/group/g2-vs-bds-mwweoplmx4',
    'https://ballchasing.com/group/flcn-vs-oxg-b0qc0bywxr',
    'https://ballchasing.com/group/g2-vs-fur-rxa5bsqwbx',
    'https://ballchasing.com/group/bds-vs-flcn-5mbqpljhbt',
    'https://ballchasing.com/group/kc-vs-g2-azjt2eb4ps',
    'https://ballchasing.com/group/g2-vs-bds-hwbf2eyolb'
]
authkey = "Auth Key Here"

pdfs = []
tdfs = []
gbgdfs = []
iddfs = []
gmsdfs = []

#Loop performing scrape functions on each group
for i in range (0,len(groups)):
    pdfs.append(bc.scrape_player_stats(groups[i],authkey))
    tdfs.append(bc.scrape_team_stats(groups[i],authkey))
    gbgdfs.append(bc.scrape_game_by_game_stats(groups[i],authkey))
    iddfs.append(bc.scrape_replay_ids(groups[i],authkey))

res = input("What would you like to name the stats directory?")

#Creates a directory based on the above input function
try:
    os.mkdir(res)
except FileExistsError:
    ""

#Local export to a csv file
pstats = pd.concat(pdfs)
tstats = pd.concat(tdfs)
gbgstats = pd.concat(gbgdfs)
ids = pd.concat(iddfs)

pstats.to_csv(res+"/"+res+"_pstats.csv",index=False)
tstats.to_csv(res+"/"+res+"_tstats.csv",index=False)
gbgstats.to_csv(res+"/"+res+"_gbgstats.csv",index=False)
ids.to_csv(res+"/"+res+"_replayids.csv",index=False)

```

## Ballchasing.com API

For documentation on the Ballchasing API, see the following link: "https://ballchasing.com/doc/api". 

You must provide an authentication key from Ballchasing.com in order to use this package.  You may generate one at "https://ballchasing.com/upload" after logging in.
