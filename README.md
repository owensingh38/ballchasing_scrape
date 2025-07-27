# Ballchasing Scrape

Ballchasing_Scrape is a Python package for scraping information and stats from Rocket League replays hosted on ballchasing.com.

## Installation

Use the pip to install Ballchasing_Scrape.

```bash
pip install ballchasing_scrape
```

## Usage
Sample script collecting stats from replays uploaded by RLCS Referee on ballchasing.com and exporting them to the local drive.

First, store your API key as an environment variable
```bash
$env:BALLCHASING_API_KEY = "YOUR_API_KEY"
```

```python
import pandas as pd
import ballchasing_scrape as bc
import os

#Query Parameters
param = {
    "uploader": 76561199225615730
}

#Load ballchasing.com API Key

authkey = os.getenv('BALLCHASING_API_KEY')
head = {
    'Authorization':  authkey
    }

#Scraping stats from returned replays
#Empty argument for 'groupurl' may be used when searching for replays not in a specific group
df = bc.scrape_game_by_game_stats("",authkey,param=param)

res = input("What would you like to name the stats directory?")

#Creates a directory based on the above input function
try:
    os.mkdir(res)
except FileExistsError:
    ""

#Local export to a csv file
df.to_csv(res+"/"+res+"_pstats.csv",index=False)

```

## Ballchasing.com API

For documentation on the Ballchasing API, see the following link: "https://ballchasing.com/doc/api".  The documentation provides parameters which may be used with functions in this package (pass parameters through the argument with "param=" in the same way you would with a standard API call).

You must provide an authentication key from Ballchasing.com in order to use this package.  You may generate one at "https://ballchasing.com/upload" after logging in.