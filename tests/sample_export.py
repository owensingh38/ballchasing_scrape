import pandas as pd
import ballchasing_scrape as bc
import os

#Query Parameters
param = {
    "uploader": 76561199225615730
}

#Insert authkey obtained from ballchasing.com here
authkey = "yaFkUF1RNMLEkaEzBJvNSVBG1w3oeq5Eb3Ofda20"
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
