def scrape_replay_ids(groupurl,authkey,verbose=bool,param={}):
    import requests
    import pandas as pd
    
    #Direct API call by group filter or replay filter
    param = param

    if groupurl != "":
        ""
    else:
        #Extract replay group ID from link
        ext = groupurl.replace("https://ballchasing.com/group/","")
        ext = ext.replace('/players-stats',"")
        ext = ext.replace('/teams-stats',"")
        ext = ext.replace('/players-games-stats',"")
        ext = ext.replace('/teams-games-stats',"")

        param.update({'group': ext})

    authkeybc = authkey
    url = "https://ballchasing.com/api/replays/"

    head = {
    'Authorization':  authkeybc
    }

    #Data request and storage
    res = requests.get(url, headers=head, params=param)
    if res.status_code == 404: 
        print("No results found...")
        return pd.DataFrame()
    data = res.json()

    #Retreive list of replay IDs
    json = pd.json_normalize(data["list"])
    id_list = list(json["id"])

    if verbose == True:
        return json
    else:
        return id_list

def scrape_game_by_game_stats(groupurl,authkey,param={}):
    import requests
    import pandas as pd
    import math

    #Direct API call by group filter or replay filter
    param = param
    req_url = ""
    message = 0

    if groupurl == "":
        req_url = ""
        ext = ""
        message = 1
        print("Beginning game by game scrape of API-returned replays")
    else:
        #Extract replay group ID from link
        ext = groupurl.replace("https://ballchasing.com/group/","")
        ext = ext.replace('/players-stats',"")
        ext = ext.replace('/teams-stats',"")
        ext = ext.replace('/players-games-stats',"")
        ext = ext.replace('/teams-games-stats',"")

        param.update({'group': ext})
        req_url = "https://ballchasing.com/group/"+ext
        print("Beginning game by game scrape of group " + ext)
    
    authkeybc = authkey
    url = "https://ballchasing.com/api/replays/"
    head = {
    'Authorization':  authkeybc
    }

    #Retreival of Group IDs
    res = scrape_replay_ids(req_url, authkeybc,param=param,verbose=True)
    if res.empty:
        print("Group not found...")
        return pd.DataFrame()
    title = list(res["replay_title"])
    duration = list(res["duration"])
    ot = list(res["overtime"])
    try: ot_s = list(res["overtime_seconds"])
    except KeyError:
        ot_s = "None"
    groups = list(res["groups"])
    games = list(res['id'])

    ggbg = []
    
    #Beginning of individual game scrape
    for i in range(0,len(games)):
        try: 
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

            gameid = games[i]
            try: groupid = groups[i][0]["id"]
            except TypeError:
                groupid = ""

            print("Beginning scrape of game " + gameid + " in group " + groupid)

            #Retreival of contextual information in the replay
            mapret = requests.get("https://ballchasing.com/api/maps",headers=head)
            maptemp = mapret.json()
            maptemp1 = pd.json_normalize(maptemp)
            maplookup = pd.DataFrame(maptemp1)
            gametitle = title[i]
            gamelink = "https://ballchasing.com/replay/"+gameid
            grouplink = "https://ballchasing.com/group/"+groupid
            datetemp = list(info['date'])
            date = datetemp[0]
            mapcodetemp = list(info['map_code'])
            mapcode = mapcodetemp[0]
            try: mapname = list(maplookup[mapcode])
            except KeyError or mapname == "":
                mapname = ""
            times = duration[i]
            ot_bool = ot[i]
            if ot_s == "None":
                ot_times = ""
            else:
                ot_times = ot_s[i]

            #Retreival of player and team information
            blue = list(info['blue.players'])
            orange = list(info['orange.players'])
            binfo = pd.DataFrame(blue[0])
            oinfo = pd.DataFrame(orange[0])
            bplayers = binfo['name']
            oplayers = oinfo['name']

            #If no column for team name exists (likely because the names were kept default in-game), then set team name to a string of players who appeared in the match
            try : bteam = list(info['blue.name'])[0]
            except KeyError:
                bttemp = " & ".join(bplayers)
                bteam = bttemp[:-1]

            try : oteam = list(info['orange.name'])[0]
            except KeyError:
                ottemp = " & ".join(oplayers)
                oteam = ottemp[:-1]

            gtitle = []
            gaid = []
            galink = []
            grid = []
            grlink = []
            t = []
            over = []
            over_secs = []
            d = []
            m = []
            
            #Blue team stats configuration
            bteamname = []
            bopponent = []

            for i in range(0,len(binfo)):
                gtitle.append(gametitle)
                gaid.append(gameid)
                galink.append(gamelink)
                grid.append(groupid)
                grlink.append(grouplink)
                try: m.append(mapname[0])
                except IndexError:
                    m.append("")
                d.append(date)
                t.append(times)
                over.append(ot_bool)
                over_secs.append(ot_times)

                bteamname.append(bteam)
                bopponent.append(oteam)
            
            bgametitle = pd.DataFrame(gtitle,columns=["game title"])
            bgameid = pd.DataFrame(gaid,columns=["game id"])
            bgamelink = pd.DataFrame(galink,columns=["game link"])
            bgroupid = pd.DataFrame(grid,columns=["group id"])
            bgrouplink = pd.DataFrame(grlink,columns=["group link"])
            bmap = pd.DataFrame(m,columns=["map"])
            bdate = pd.DataFrame(d,columns=["date"])
            bdur = pd.DataFrame(t,columns=["duration"])
            bot = pd.DataFrame(over,columns=["overtime"])
            bots = pd.DataFrame(over_secs,columns=["overtime_duration"])
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
            
            bsf = 0
            bgf = 0
            bwin = 0

            #Shots and Goals For
            for i in range(0,len(bplayers)):
                bsf = bsf + core[i]["shots"]
                bgf = bgf + core[i]["goals"]

            #Win Condition
            for i in range(0,len(bplayers)):
                if core[i]["mvp"] == True:
                    bwin = 1
                    break
                else:
                    bwin = 0

            x = pd.DataFrame()
            if bwin == 1:
                x = pd.DataFrame(["win"],columns=["result"]) 
            else:
                x = pd.DataFrame(["loss"],columns=["result"]) 

            #Adding Individual Stats for Blue
            for i in range(0,len(bplayers)):
                print("Adding stats for " + bplayers[i] + " in game " + gameid + " for " + bteam + " against " + oteam)
                stat = []
                stat.append(x)
                stat.append(pd.DataFrame([core[i]]))
                stat.append(pd.DataFrame([bsf],columns=["shots_for"]))
                stat.append(pd.DataFrame([bgf],columns=["goals_for"]))
                stat.append(pd.DataFrame([(core[i]["goals"]+core[i]["assists"])],columns=['gpar']))
                try: stat.append(pd.DataFrame([round((core[i]["goals"]+core[i]["assists"])/bgf,5)],columns=['gpar_percentage']))
                except ZeroDivisionError:
                    stat.append(pd.DataFrame([0],columns=["gpar_percentage"]))
                stat.append(pd.DataFrame([boost[i]]))
                stat.append(pd.DataFrame([positioning[i]]))
                stat.append(pd.DataFrame([movement[i]]))
                stat.append(pd.DataFrame([demos[i]]))
                df = pd.concat(stat,axis=1)
                bps.append(df)
            
            bluestats = pd.concat(bps,ignore_index=True)
            blueinfo = pd.concat([bgametitle,bgameid,bgamelink,bgroupid,bgrouplink,bdate,bmap,bdur,bot,bots,bplatform,bpid,bplayers,bcarid,bcarname,bpteam,bpopp],axis=1)
            
            bluestats.reset_index()
            blueinfo.reset_index()
            
            bluegame = pd.concat([blueinfo,bluestats],axis=1)

            gtitle = []
            gaid = []
            galink = []
            grid = []
            grlink = []
            t = []
            over = []
            over_secs = []
            d = []
            m = []

            #Orange team stats configuration
            oteamname = []
            oopponent = []

            for i in range(0,len(oinfo)):
                gtitle.append(gametitle)
                gaid.append(gameid)
                galink.append(gamelink)
                grid.append(groupid)
                grlink.append(grouplink)
                try: m.append(mapname[0])
                except IndexError:
                    m.append("")
                d.append(date)
                t.append(times)
                over.append(ot_bool)
                over_secs.append(ot_times)

                oteamname.append(oteam)
                oopponent.append(bteam)
            
            ogametitle = pd.DataFrame(gtitle,columns=["game title"])
            ogameid = pd.DataFrame(gaid,columns=["game id"])
            ogamelink = pd.DataFrame(galink,columns=["game link"])
            ogroupid = pd.DataFrame(grid,columns=["group id"])
            ogrouplink = pd.DataFrame(grlink,columns=["group link"])
            omap = pd.DataFrame(m,columns=["map"])
            odate = pd.DataFrame(d,columns=["date"])
            odur = pd.DataFrame(t,columns=["duration"])
            oot = pd.DataFrame(over,columns=["overtime"])
            oots = pd.DataFrame(over_secs,columns=["overtime_duration"])
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

            osf = 0
            ogf = 0

            #Shots and Goals For
            for i in range(0,len(bplayers)):
                osf = osf + core[i]["shots"]
                ogf = ogf + core[i]["goals"]

            x = pd.DataFrame()
            if bwin == 1:
                x = pd.DataFrame(["loss"],columns=["result"]) 
            else:
                x = pd.DataFrame(["win"],columns=["result"]) 

            #Adding Individual Stats for Oeange
            for i in range(0,len(oplayers)):
                stat = []
                print("Adding stats for " + oplayers[i] + " in game " + gameid + " for " + oteam + " against " + bteam)
                stat.append(x)
                stat.append(pd.DataFrame([core[i]]))
                stat.append(pd.DataFrame([osf],columns=["shots_for"]))
                stat.append(pd.DataFrame([ogf],columns=["goals_for"]))
                stat.append(pd.DataFrame([(core[i]["goals"]+core[i]["assists"])],columns=['gpar']))
                try: stat.append(pd.DataFrame([round((core[i]["goals"]+core[i]["assists"])/ogf,5)],columns=['gpar_percentage']))
                except ZeroDivisionError:
                    stat.append(pd.DataFrame([0],columns=["gpar_percentage"]))
                stat.append(pd.DataFrame([boost[i]]))
                stat.append(pd.DataFrame([positioning[i]]))
                stat.append(pd.DataFrame([movement[i]]))
                stat.append(pd.DataFrame([demos[i]]))
                df = pd.concat(stat,axis=1)
                ops.append(df)

            orangestats = pd.concat(ops,ignore_index=True)
            orangeinfo = pd.concat([ogametitle,ogameid,ogamelink,ogroupid,ogrouplink,odate,omap,odur,oot,oots,oplatform,opid,oplayers,ocarid,ocarname,opteam,opopp],axis=1)
            
            orangestats.reset_index()
            orangeinfo.reset_index()
            
            orangegame = pd.concat([orangeinfo,orangestats],axis=1)

            #Building the stats table
            gamestats = pd.concat([bluegame,orangegame])

            print("Finished scrape for " + gameid + " in group " + groupid + " between " + bteam + " and " + oteam + "\n")

            ggbg.append(gamestats)
        except:
            print("\nAn error occured, skipping this replay...\n")
            pass

    #Concatenate all scraped games into a single table and return the table
    groupgbg = pd.concat(ggbg)
    groupgbg.rename(columns={"inflicted":"demos inflicted","taken":"demos taken"})
    groupgbg = groupgbg.sort_values(by=['date','team',"name","id"],ascending=True)
    
    if message == 1:
        print("Finished scrape of API-returned replays\n")
    else:
        print("Finished scrape of group "+ext+"\n")

    return groupgbg

def player_group_stats_parser(scrape,loc="", by_group=bool, groupurl="",authkey="",param={}):
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

        df = scrape_game_by_game_stats(groupurl,authkey,param=param)
        
    #Error Handling
    try: df['name']
    except KeyError: 
        return pd.DataFrame()
    
    df = df.replace("win",1)
    df = df.replace("loss",0)

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

    if by_group == False:
        info = pd.DataFrame([platform,pid,players,car_id,car_name,gp],index=["platform","id","name","car_id","car_name","games_played"])
    else:
        info = pd.DataFrame([id,link,platform,pid,players,car_id,car_name,team,opp,gp],index=["group id","group link","platform","id","name","car_id","car_name","team","opponent","games_played"])
    info = info.transpose()

    print("Parsing game by game stats to group stats in group " + ext)
    stats = []
    col = df.columns.tolist()
    keys = []

    #Filter unwanted keys
    for i in range(0,len(col)):
        if "percent" not in col[i] and i>=17:
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
    all.rename(columns={'result': 'wins'},inplace=True)
    info = info.reset_index(drop=True)
    all = all.reset_index(drop=True)

    gstats = pd.concat([info,all],axis=1)
    
    return gstats