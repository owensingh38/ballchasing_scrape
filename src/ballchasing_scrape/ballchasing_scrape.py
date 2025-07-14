import requests as rs
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

### BALLCHASING SCRAPE ###

## GLOBAL VARIABLES ##
stats_col = ['game_id','game_date','game_link','replay_id','team_size','game_title','map_code','duration','overtime','overtime_seconds',
             'platform', 'steering_sensitivity','fov', 'height', 'pitch', 'distance', 'stiffness', 'swivel_speed', 'transition_speed', 
             'car_id','car_name','id','name','team','opponent',
             'start_time','end_time','time_on_field','mvp',
             'shots', 'shots_for', 'shots_against', 'goals', 'goals_for', 'goals_against', 'saves', 'assists', 'score', 'shooting_percentage', 
             'bpm', 'bcpm', 'avg_amount', 'amount_collected', 'amount_stolen', 'amount_collected_big', 'amount_stolen_big', 'amount_collected_small', 'amount_stolen_small', 
             'count_collected_big', 'count_stolen_big', 'count_collected_small', 'count_stolen_small', 'amount_overfill', 'amount_overfill_stolen', 'amount_used_while_supersonic', 
             'time_zero_boost', 'percent_zero_boost', 'time_full_boost', 'percent_full_boost', 'time_boost_0_25', 'time_boost_25_50', 'time_boost_50_75', 'time_boost_75_100', 
             'percent_boost_0_25', 'percent_boost_25_50', 'percent_boost_50_75', 'percent_boost_75_100', 
             'avg_speed', 'total_distance', 'time_supersonic_speed', 'time_boost_speed', 'time_slow_speed', 'time_ground', 'time_low_air', 'time_high_air', 'time_powerslide', 
             'count_powerslide', 'avg_powerslide_duration', 'avg_speed_percentage', 'percent_slow_speed', 'percent_boost_speed', 'percent_supersonic_speed', 'percent_ground', 'percent_low_air', 'percent_high_air', 'avg_distance_to_ball', 'avg_distance_to_ball_possession', 'avg_distance_to_ball_no_possession', 'avg_distance_to_mates', 'time_defensive_third', 'time_neutral_third', 'time_offensive_third', 'time_defensive_half', 'time_offensive_half', 'time_behind_ball', 'time_infront_ball', 'time_most_back', 'time_most_forward', 'goals_against_while_last_defender', 'time_closest_to_ball', 'time_farthest_from_ball', 
             'percent_defensive_third', 'percent_offensive_third', 'percent_neutral_third', 'percent_defensive_half', 'percent_offensive_half', 
             'percent_behind_ball', 'percent_infront_ball', 'percent_most_back', 'percent_most_forward', 'percent_closest_to_ball', 'percent_farthest_from_ball',
             'inflicted','taken']

# POST FUNCTIONS #
#Post Functions
def post_replay(file_path, authkey, visibility="public", groupid=""):
    #Prepare upload request
    url = "https://ballchasing.com/api/v2/upload"
    file = {"file":open(file_path,"rb")}
    
    head = {
        'Authorization':  authkey
    }

    param = {
        "visibility": visibility,
    }
    if groupid != "":
        param.update({"group": groupid})

    #Upload request
    res = rs.post(url,headers=head,data=param,files=file)

    #Assess API response
    if res.status_code == 201:
        # Upload successful
        print("Replay upload successful\nView here: " + "https://ballchasing.com/replay/"+res.json()['id'])
        return res.json()['id']
    elif res.status_code == 409:
        # Upload already exists
        print("Replay already exists\nView here: " + "https://ballchasing.com/replay/"+res.json()['id'])
        return res.json()['id']
    else:
        # Error occured
        print("An error occured...\n")
        res.raise_for_status()

def post_group(name, authkey, parent_id="",p_id="by-id",t_id="by-distinct-players"):
    #Prepare upload request
    url = "https://ballchasing.com/api/groups"
    
    head = {
        'Authorization':  authkey
    }

    param = {
        "name": name,
        "player_identification": p_id,
        "team_identification": t_id
    }

    if parent_id != "":
        param.update({"parent": parent_id})

    #Upload request
    res = rs.post(url,headers=head,json=param)

    #Assess API response
    if res.status_code == 201:
        # Upload successful
        print("Group upload successful\nView here: " + "https://ballchasing.com/group/"+res.json()['id'])
        return res.json()['id']
    elif res.status_code == 409:
        # Upload already exists
        print("Group already exists\nView here: " + "https://ballchasing.com/group/"+res.json()['id'])
        return res.json()['id']
    else:
        # Error occured
        print("An error occured...\n")
        res.raise_for_status()


# SCRAPE FUNCTIONS #
def extract_id(groupurl):
    #Extract replay group ID from link

    for repl in ['https://ballchasing.com/group/','/players-stats','/teams-stats','/players-games-stats','/teams-games-stats']:
        groupurl = groupurl.replace(repl,"")

    return groupurl

def scrape_file_structure(groupurl,authkey,groups,param={}):
    #Direct API call by group filter or replay filter
    id = extract_id(groupurl)
    
    url = 'https://ballchasing.com/api/groups/'
    head = {
        'Authorization':  authkey
    }
    param.update({'group': id})

    #Data request and storage
    res = rs.get(url, headers=head, params=param)
    if res.status_code == 404: 
        print("No results found...")
        return pd.DataFrame()
    data = res.json()
    
    groups.append(id)

    for sub_group in data["list"]:
        if sub_group['direct_replays'] > 0:
            groups.append(sub_group['id'])
            print("Adding groups from group " + sub_group['id'])
        else:
            scrape_file_structure(sub_group['id'],authkey,groups)
            print("Searching through sub-group " + sub_group['id'])

def scrape_replay_ids(groups,authkey,param={}):
    #Direct API call by group filter or replay filter
    url = "https://ballchasing.com/api/replays/"

    head = {
        'Authorization':  authkey
    }

    ids = []
    for group in groups:
        param.update({'group': group})
        #Data request and storage
        res = rs.get(url, headers=head, params=param)
        if res.status_code == 404: 
            print("No results found...")
            return pd.DataFrame()
        data = res.json()

        #Retreive list of replay IDs
        json = pd.json_normalize(data["list"])
        if json.empty:
            continue
        else:
            ids = ids + json["id"].to_list()

    return ids

def scrape_group(groupurl,authkey,param={}):
    #Given ballchasing group url and authkey, return stats at game level

    #Search for all sub groups at url
    groups = []
    scrape_file_structure(groupurl,authkey,groups,param)

    #Now retreieve the individual match ids from each group
    games = scrape_replay_ids(groups,authkey)

    url = "https://ballchasing.com/api/replays/"

    head = {
        'Authorization':  authkey
    }
    
    #Now begin scraping stats
    print(f'Scraping game-level stats for games in {groups}')
    stats = []
    for game in games:
        print(f'Scraping data from game: {game}')
        data = rs.get(url+game,headers=head).json()

        try:
            print(f'Error: {data['error']}')
            continue
        except:
        #Check if team name exists (if not then assign a name)
            for team_color in ['blue','orange']:
                try: data[team_color]['name']
                except:
                    data[team_color]['name'] = team_color.upper()

            #Stats columns
            blue = pd.json_normalize(data['blue']['players'])
            blue['team'] = data['blue']['name']
            blue['opponent'] = data['orange']['name']
            
            orange = pd.json_normalize(data['orange']['players'])
            orange['team'] = data['orange']['name']
            orange['opponent'] = data['blue']['name']

            blue['goals_for'] = blue['stats.core.goals'].sum()
            blue['shots_for'] = blue['stats.core.shots'].sum()
            orange['goals_for'] = orange['stats.core.goals'].sum()
            orange['shots_for'] = orange['stats.core.shots'].sum()

            df = pd.concat([blue,orange])

            #Info columns
            df['game_id'] = game
            df['game_date'] = data['date']
            df['game_link'] = data['link']
            df['replay_id'] = data['rocket_league_id']
            df['game_title'] = data['title']
            df['team_size'] = data['team_size']
            df['map_code'] = data['map_code']
            df['duration'] = data['duration']
            df['overtime'] = data['overtime']
            
            try:
                df['overtime_seconds'] = data['overtime_seconds']
            except:
                df['overtime_seconds'] = None
            
            stats.append(df)

    stats_df = pd.concat(stats).drop(columns=['mvp']).fillna(0)

    #Clean and organize stats\
    col = stats_df.columns
    change = stats_df.columns
    for repl in ['id.','camera.','stats.core.','stats.boost.','stats.movement.','stats.positioning.','stats.demo.']:
        change = change.str.replace(repl,'')

    col_name = dict(zip(col.to_list(),change.to_list()))
    stats_df = stats_df.rename(columns=col_name)

    stats_df['time_on_field'] = stats_df['end_time']-stats_df['start_time']

    return stats_df[[col for col in stats_col if col in stats_df.columns.to_list()]]

# AGG FUNCTIONS #
def calc_stats(df,group=['id','team']):
    def mode(series):
        return series.mode().iloc[0]

    stats = df.groupby(group).agg(
        name=('name',mode),
        car_name=('car_name',mode),
        games_played=('game_id','nunique'),
        time_on_field=('time_on_field','sum'),
        mvp=('mvp',lambda x: (x).sum()),
        shots=('shots','sum'),
        shots_for=('shots_for','sum'),
        shots_against=('shots_against','sum'),
        goals=('goals','sum'),
        goals_for=('goals_for','sum'),
        goals_against=('goals_against','sum'),
        saves=('saves','sum'),
        assists=('assists','sum'),
        score=('score','sum'),
        amount_collected=('amount_collected','sum'),
        amount_stolen=('amount_stolen','sum'),
        amount_collected_big=('amount_collected_big','sum'),
        amount_stolen_big=('amount_stolen_big','sum'),
        amount_collected_small=('amount_collected_small','sum'),
        amount_stolen_small=('amount_stolen_small','sum'),
        count_collected_big=('count_collected_big','sum'),
        count_stolen_big=('count_stolen_big','sum'),
        count_collected_small=('count_collected_small','sum'),
        count_stolen_small=('amount_stolen_small','sum'),
        amount_overfill=('amount_overfill','sum'),
        amount_overfill_stolen=('amount_overfill_stolen','sum'),
        amount_used_while_supersonic=('amount_overfill_stolen','sum'),
        time_zero_boost=('time_zero_boost','sum'),
        time_full_boost=('time_zero_boost','sum'),
        time_boost_0_25=('time_boost_0_25','sum'),
        time_boost_25_50=('time_boost_25_50','sum'),
        time_boost_50_75=('time_boost_50_75','sum'),
        time_boost_75_100=('time_boost_75_100','sum'),
        total_distance=('total_distance','sum'),
        time_supersonic_speed=('time_supersonic_speed','sum'),
        time_boost_speed=('time_boost_speed','sum'),
        time_slow_speed=('time_slow_speed','sum'),
        time_ground=('time_ground','sum'),
        time_low_air=('time_low_air','sum'),
        time_high_air=('time_high_air','sum'),
        time_powerslide_=('time_powerslide','sum'),
        count_powerslide_=('count_powerslide','sum'),
        time_defensive_third=('time_defensive_third','sum'),
        time_neutral_third=('time_neutral_third','sum'),
        time_offensive_third=('time_offensive_third','sum'),
        time_defensive_half=('time_defensive_half','sum'),
        time_offensive_half=('time_offensive_third','sum'),
        time_behind_ball=('time_defensive_third','sum'),
        time_infront_ball=('time_neutral_third','sum'),
        time_most_back=('time_offensive_third','sum'),
        time_most_forward=('time_defensive_half','sum'),
        goals_against_while_last_defender=('goals_against_while_last_defender','sum'),
        time_closest_to_ball=('time_offensive_third','sum'),
        time_farthest_to_ball=('time_offensive_third','sum'),
        inflicted=('inflicted','sum'),
        taken=('taken','sum'),
    ).reset_index()

    for stat in stats.columns[(len(group)+5):len(stats.columns)]:
        stats[f'{stat}_per_game'] = stats[stat]/stats['games_played']

    stats['shooting_percentage'] = stats['goals']/stats['shots']
    stats['gpar'] = stats['goals']+stats['assists']
    stats['gpar_percentage'] = stats['gpar']/stats['goals_for']

    stats['rating'] = (
        stats['shots_per_game']/(stats['shots']/stats['games_played']) +
        stats['goals_per_game']/(stats['goals']/stats['games_played']) +
        stats['saves_per_game']/(stats['saves']/stats['games_played']) +
        stats['assists_per_game']/(stats['assists']/stats['games_played']) +
        stats['score_per_game']/(stats['score']/stats['games_played']) +
        stats['shooting_percentage']/(stats['goals']/stats['shots']) +
        stats['gpar_percentage']/(stats['goals']/stats['goals_for'])
    )/7

    if 'id' or 'name' not in group:
        stats = stats.drop(columns=['name','mvp',
                                    'shots_for','goals_for',
                                    'shots_for_per_game','goals_for_per_game',
                                    'assists','car_name',
                                    'gpar','gpar_percentage',
                                    'rating']).rename(columns={'shots':'shots_for',
                                                                               'goals':'goals_for'}, errors='ignore')

    return stats

# MISC FUNCTIONS #
def ping_api(authkey):
    url = "https://ballchasing.com/api/"
    authkeybc = authkey
    
    head = {
        'Authorization':  authkeybc
    }

    res = rs.get(url,headers=head)

    if res.status_code == 200:
        print("API reachable...\n")
        return res.json()
    if res.status_code == 401:
        print("Missing API key...\n")
        return res.json()["error"]
    if res.status_code == 500:
        print(res.json()["error"])
        return res.json()["error"]