def scrape_replay_ids(groupurl,authkey):
    import requests
    import pandas as pd
    
    #Extract replay group ID from link
    ext = groupurl.replace("https://ballchasing.com/group/","")
    ext = ext.replace('/players-stats',"")
    ext = ext.replace('/teams-stats',"")
    ext = ext.replace('/players-games-stats',"")
    ext = ext.replace('/teams-games-stats',"")

    authkeybc = authkey
    url = "https://ballchasing.com/api/replays/"

    head = {
    'Authorization':  authkeybc
    }

    param = {
    'group': ext
    }

    #Data request and storage
    res = requests.get(url, headers=head, params=param)
    if res.status_code == 404: 
        print("Group not found...")
        return pd.DataFrame()
    data = res.json()

    #Retreive list of replay IDs
    list = pd.json_normalize(data["list"])

    return list
 

def scrape_player_stats(groupurl,authkey):
    import requests
    import pandas as pd

    #Extract replay group ID from link
    ext = groupurl.replace("https://ballchasing.com/group/","")
    ext = ext.replace('/players-stats',"")
    ext = ext.replace('/teams-stats',"")
    ext = ext.replace('/players-games-stats',"")
    ext = ext.replace('/teams-games-stats',"")

    print("Adding player stats for "+ ext + "...")

    authkeybc = authkey
    url = "https://ballchasing.com/api/groups/"+ext

    head = {
    'Authorization':  authkeybc
    }

    #Data request and storage
    res = requests.get(url, headers=head)
    if res.status_code == 404:
        print("Group not found...")
        return pd.DataFrame()
    data = res.json()

    #Retreive player stats
    pstats = pd.json_normalize(data['players'])
    inter = pd.json_normalize(data)
    gid = list(inter['id'])
    groupid = []
    grouplink = []

    p = list(pstats["name"])
    t = list(pstats["team"])

    #Create columns for group ID and group link for the table
    for i in range(0,len(p)):
        groupid.append(gid[0])
        grouplink.append("https://ballchasing.com/group/"+gid[0])
        print("Added stats for " + p[i] + " on " + t[i])

    pstats.insert(0, "group id", groupid)
    pstats.insert(1, "group link", grouplink)
    pstats = pstats.drop(pstats.iloc[:,88:len(pstats)],axis = 1)

    return pstats

def scrape_team_stats(groupurl,authkey):
    import requests
    import pandas as pd

    #Extract replay group ID from link
    ext = groupurl.replace("https://ballchasing.com/group/","")
    ext = ext.replace('/players-stats',"")
    ext = ext.replace('/teams-stats',"")
    ext = ext.replace('/players-games-stats',"")
    ext = ext.replace('/teams-games-stats',"")
    print("Adding team stats for "+ ext + "...")

    authkeybc = authkey
    url = "https://ballchasing.com/api/groups/"+ext

    head = {
    'Authorization':  authkeybc
    }

    #Data request and storage
    res = requests.get(url, headers=head)
    if res.status_code == 404:
        print("Group not found...")
        return pd.DataFrame()
    data = res.json()
    inter = pd.json_normalize(data)
    gid = list(inter['id'])
    groupid = []
    grouplink = []

    #Retreive team stats
    tstats = pd.json_normalize(data['teams'])

    t = list(tstats["name"])

    #Create columns for group ID and group link for the table
    for i in range(0,len(t)):
        groupid.append(gid[0])
        grouplink.append("https://ballchasing.com/group/"+gid[0])
        print("Added stats for " + t[i])

    tstats.insert(0, "group id", groupid)
    tstats.insert(1, "group link", grouplink)
    tstats = tstats.drop(tstats.iloc[:,58:len(tstats)],axis = 1)
    tstats = tstats.drop(["players"],axis=1)

    return tstats

def scrape_game_by_game_stats(groupurl,authkey):
    import requests
    import pandas as pd

    #Extract replay group ID from link
    ext = groupurl.replace("https://ballchasing.com/group/","")
    ext = ext.replace('/players-stats',"")
    ext = ext.replace('/teams-stats',"")
    ext = ext.replace('/players-games-stats',"")
    ext = ext.replace('/teams-games-stats',"")
    authkeybc = authkey
    url = "https://ballchasing.com/api/replays/"
    head = {
    'Authorization':  authkeybc
    }

    print("Beginning game by game scrape of group " + ext)

    #Retreival of Group IDs
    res = scrape_replay_ids("https://ballchasing.com/group/"+ext, authkeybc)
    if res.empty:
        print("Group not found...")
        return pd.DataFrame()
    games = list(res['id'])

    ggbg = []
    
    #Beginning of individual game scrape
    for i in range(0,len(games)):
        res = requests.get(url+games[i],headers=head)
        if res.status_code == 404:
            print("Game not found...")
            return pd.DataFrame()
        data = res.json()
        info = pd.json_normalize(data)
        
        #Group scrape is terminated if no data is present in the group request
        if info.empty:
            "Game-by-game stats can not be scraped, as their are no replays immediately filed under this group ID (it is the parent of one or more groups with no replays in its root directory)."
            return pd.DataFrame()

        print("Beginning scrape of game " + games[i] + " in group " + ext)

        #Retreival of contextual information in the replay
        mapret = requests.get("https://ballchasing.com/api/maps",headers=head)
        maptemp = mapret.json()
        maptemp1 = pd.json_normalize(maptemp)
        maplookup = pd.DataFrame(maptemp1)
        gameid = games[i]
        gamelink = "https://ballchasing.com/replay/"+gameid
        groupid = ext
        grouplink = groupurl
        datetemp = list(info['date'])
        date = datetemp[0]
        mapcodetemp = list(info['map_code'])
        mapcode = mapcodetemp[0]
        try: mapname = list(maplookup[mapcode])
        except KeyError or mapname == "":
            mapname = ""
        
        #Retreival of player and team information
        blue = list(info['blue.players'])
        orange = list(info['orange.players'])
        binfo = pd.DataFrame(blue[0])
        oinfo = pd.DataFrame(orange[0])
        bplayers = binfo['name']
        oplayers = oinfo['name']

        #If no column for team name exists (likely because the names were kept default in-game), then set team name to a string of players who appeared in the match
        try : bteam = list(info['blue.name'])
        except KeyError:
            bttemp = " & ".join(bplayers)
            bteam = bttemp[:-1]

        try : oteam = list(info['orange.name'])
        except KeyError:
            ottemp = " & ".join(oplayers)
            oteam = ottemp[:-1]

        gaid = []
        galink = []
        grid = []
        grlink = []
        m = []

        #Blue team stats configuration
        bteamname = []
        bopponent = []
        d = []

        for i in range(0,len(binfo)):
            gaid.append(gameid)
            galink.append(gamelink)
            grid.append(groupid)
            grlink.append(grouplink)
            try: m.append(mapname[0])
            except IndexError:
                m.append("")
            d.append(date)

            bteamname.append(bteam)
            bopponent.append(oteam)
        
        bgameid = pd.DataFrame(gaid,columns=["game id"])
        bgamelink = pd.DataFrame(galink,columns=["game link"])
        bgroupid = pd.DataFrame(grid,columns=["group id"])
        bgrouplink = pd.DataFrame(grlink,columns=["group link"])
        bmap = pd.DataFrame(m,columns=["map"])
        bdate = pd.DataFrame(d,columns=["date"])
        bpteam = pd.DataFrame(bteamname,columns=["team"])
        bpopp = pd.DataFrame(bopponent,columns=["opponent"])

        
        bid = list(binfo['id'])
        temp = pd.DataFrame(bid)
        bplatform = temp['platform']
        bpid = temp['id']
        bcarid = binfo['car_id']
        bcarname = binfo['car_name']
        bstats = list(binfo['stats'])
        
        df = pd.DataFrame(bstats)
        core = df['core']
        boost = df['boost']
        positioning = df['positioning']
        movement = df['movement']
        demos = df['demo']

        bps = []
        
        sf = 0
        gf = 0

        #Shots and Goals For
        for i in range(0,len(bplayers)):
            sf = sf + core[i]["shots"]
            gf = gf + core[i]["goals"]

        #Adding Individual Stats for Blue
        for i in range(0,len(bplayers)):
            print("Adding stats for " + bplayers[i] + " in game " + gameid + " for " + bteam[0] + " against " + oteam[0])
            stat = []
            stat.append(pd.DataFrame([core[i]]))
            stat.append(pd.DataFrame([sf],columns=["shots for"]))
            stat.append(pd.DataFrame([gf],columns=["goals for"]))
            stat.append(pd.DataFrame([(core[i]["goals"]+core[i]["assists"])],columns=['gpar']))
            try: stat.append(pd.DataFrame([round((core[i]["goals"]+core[i]["assists"])/gf,5)],columns=['gpar_percentage']))
            except ZeroDivisionError:
                stat.append(pd.DataFrame([0],columns=["gpar_percentage"]))

            stat.append(pd.DataFrame([boost[i]]))
            stat.append(pd.DataFrame([positioning[i]]))
            stat.append(pd.DataFrame([movement[i]]))
            stat.append(pd.DataFrame([demos[i]]))
            df = pd.concat(stat,axis=1)
            bps.append(df)
        
        bluestats = pd.concat(bps,ignore_index=True)
        blueinfo = pd.concat([bgameid,bgamelink,bgroupid,bgrouplink,bdate,bmap,bplatform,bpid,bplayers,bcarid,bcarname,bpteam,bpopp],axis=1)
        
        bluestats.reset_index()
        blueinfo.reset_index()
        
        bluegame = pd.concat([blueinfo,bluestats],axis=1)

        gaid = []
        galink = []
        grid = []
        grlink = []
        m = []
        d = []

        #Orange team stats configuration
        oteamname = []
        oopponent = []

        for i in range(0,len(oinfo)):
            gaid.append(gameid)
            galink.append(gamelink)
            grid.append(groupid)
            grlink.append(grouplink)
            try: m.append(mapname[0])
            except IndexError:
                m.append("")
            d.append(date)

            oteamname.append(oteam)
            oopponent.append(bteam)
        
        ogameid = pd.DataFrame(gaid,columns=["game id"])
        ogamelink = pd.DataFrame(galink,columns=["game link"])
        ogroupid = pd.DataFrame(grid,columns=["group id"])
        ogrouplink = pd.DataFrame(grlink,columns=["group link"])
        omap = pd.DataFrame(m,columns=["map"])
        odate = pd.DataFrame(d,columns=["date"])
        opteam = pd.DataFrame(oteamname,columns=["team"])
        opopp = pd.DataFrame(oopponent,columns=["opponent"])

        oid = list(oinfo['id'])
        temp = pd.DataFrame(oid)
        oplatform = temp['platform']
        opid = temp['id']
        ocarid = oinfo['car_id']
        ocarname = oinfo['car_name']
        ostats = list(oinfo['stats'])
        
        df = pd.DataFrame(ostats)
        core = df['core']
        boost = df['boost']
        positioning = df['positioning']
        movement = df['movement']
        demos = df['demo']

        ops = []

        sf = 0
        gf = 0

        #Shots and Goals For
        for i in range(0,len(bplayers)):
            sf = sf + core[i]["shots"]
            gf = gf + core[i]["goals"]

        #Adding Individual Stats for Oeange
        for i in range(0,len(bplayers)):
            stat = []
            print("Adding stats for " + oplayers[i] + " in game " + gameid + " for " + oteam[0] + " against " + bteam[0])
            stat.append(pd.DataFrame([core[i]]))
            stat.append(pd.DataFrame([sf],columns=["shots for"]))
            stat.append(pd.DataFrame([gf],columns=["goals for"]))
            stat.append(pd.DataFrame([(core[i]["goals"]+core[i]["assists"])],columns=['gpar']))
            try: stat.append(pd.DataFrame([round((core[i]["goals"]+core[i]["assists"])/gf,5)],columns=['gpar_percentage']))
            except ZeroDivisionError:
                stat.append(pd.DataFrame([0],columns=["gpar_percentage"]))
            stat.append(pd.DataFrame([boost[i]]))
            stat.append(pd.DataFrame([positioning[i]]))
            stat.append(pd.DataFrame([movement[i]]))
            stat.append(pd.DataFrame([demos[i]]))
            df = pd.concat(stat,axis=1)
            ops.append(df)

        orangestats = pd.concat(ops,ignore_index=True)
        orangeinfo = pd.concat([ogameid,ogamelink,ogroupid,ogrouplink,odate,omap,oplatform,opid,oplayers,ocarid,ocarname,opteam,opopp],axis=1)
        
        orangestats.reset_index()
        orangeinfo.reset_index()
        
        orangegame = pd.concat([orangeinfo,orangestats],axis=1)

        #Building the stats table
        gamestats = pd.concat([bluegame,orangegame])

        print("Finished scrape for " + gameid + " in group " + groupid + "between " + bteam[0] + " and " + oteam[0])

        ggbg.append(gamestats)

    #Concatenate all scraped games into a single table and return the table
    groupgbg = pd.concat(ggbg)
    groupgbg.rename(columns={"inflicted":"demos inflicted","taken":"demos taken"})
    groupgbg = groupgbg.sort_values(by=['date','team',"name","id"],ascending=True)
    
    print("Finished scrape of group "+ext)

    return groupgbg

def player_group_stats_parser(scrape,loc="",groupurl="",authkey=""):
    import pandas as pd
    
    #Routs program to read local file or to scrape data live
    if scrape == False:
        df = pd.read_csv(loc)
        ext = list(df['group id'])
        ext = ext[0]
    else: 
        ext = groupurl.replace("https://ballchasing.com/group/","")
        ext = ext.replace('/players-stats',"")
        ext = ext.replace('/teams-stats',"")
        ext = ext.replace('/players-games-stats',"")
        ext = ext.replace('/teams-games-stats',"")

        df = scrape_game_by_game_stats(groupurl,authkey)

    #Stat Generation
    players = df['name'].unique()
    group_id = df['group id'].tolist()
    group_id = group_id[0]
    group_link = df['group link'].tolist()
    group_link = group_link[0]
    id = []
    link = []
    team = []
    opp = []
    platform = []
    pid = []
    car_id = []
    car_name = []
    gp = []
    
    #Info dataframe creation
    for i in range(0, len(players)):
        gp.append(df['name'].value_counts().get(players[i],0))
        
    for i in range(0,len(players)):
        id.append(group_id)
        link.append(group_link)
        team.append(df.loc[df["name"] == players[i], "team"].tolist()[0])
        opp.append(df.loc[df["name"] == players[i], "opponent"].tolist()[0])
        platform.append(df.loc[df["name"] == players[i], "platform"].tolist()[0])
        pid.append(df.loc[df["name"] == players[i], "id"].tolist()[0])
        car_id.append(df.loc[df["name"] == players[i], "car_id"].tolist()[0])
        car_name.append(df.loc[df["name"] == players[i], "car_name"].tolist()[0])

    info = pd.DataFrame([id,link,platform,pid,players,car_id,car_name,team,opp,gp],index=["group id","group link","platform","id","name","car_id","car_name","team","opponent","games_played"])
    info = info.transpose()

    print("Parsing game by game stats to group stats in group " + ext)
    stats = []
    col = df.columns.tolist()
    keys = []

    #Filter unwanted keys
    for i in range(0,len(col)):
        if "percent" not in col[i] and i>=13:
            keys.append(col[i])

    #Sum stats in game-by-game frame by iterating through columns and retaining keys
    for i in range(0,len(players)):
        print("Adding player "+players[i]+" on "+team[i]+" in group "+group_id)
        temp = []
        for j in keys:
            temp.append(df.loc[df["name"] == players[i], j].sum())
        
        stats.append(pd.DataFrame(temp,index=keys))

    #Data organization
    all = pd.concat(stats,axis=1)
    all = all.transpose()
    info = info.reset_index(drop=True)
    all = all.reset_index(drop=True)

    gstats = pd.concat([info,all],axis=1)
    
    return gstats
