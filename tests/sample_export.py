import pandas as pd
import ballchasing_scrape as bc
import os

#Stats import
groups = [
    'https://ballchasing.com/group/fc-barcha-vs-bastard-munchen-qgmna4nqh9',
    'https://ballchasing.com/group/blue-lock-season-hzptzik95z',
    'https://ballchasing.com/group/rm-series-project-v-l7665k7q2m',
    'https://ballchasing.com/group/pxg-v-ars-pmse9zychi',
    'https://ballchasing.com/group/manshine-united-vs-marseille-fbgfufmb4m',
    'https://ballchasing.com/group/manshine-united-vs-ajajax-b1pl2ryk7n'
]

#Insert authkey obtained from ballchasing.com here
authkey = "yaFkUF1RNMLEkaEzBJvNSVBG1w3oeq5Eb3Ofda20"
head = {
    'Authorization':  authkey
    }
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