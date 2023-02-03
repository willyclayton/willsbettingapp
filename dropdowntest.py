import pandas as pd
import requests
import math
import streamlit as st
from datetime import datetime, timedelta
#hello there
#this is another update?
#print('do something now hahaha')



def get_all_teams2():
    url = "https://v1.hockey.api-sports.io/games?league=57&season=2022"

    payload={}
    headers = {
      'x-rapidapi-key': '96b4e9553b3b604fcf5d4f392bac9c23',
      'x-rapidapi-host': 'v1.hockey.api-sports.io'
    }

    teams = requests.request("GET", url, headers=headers, data=payload)

    raw_teams = teams.json()
    raw_teams = raw_teams['response']

    homeTeam = []
    homeTeamID = []
    awayTeam = []
    awayTeamID = []
    UTCTime = []
    ESTTime = []

    for i in raw_teams:
        homeTeam.append(i['teams']['home']['name'])
        homeTeamID.append(i['teams']['home']['id'])
        awayTeam.append(i['teams']['away']['name'])
        awayTeamID.append(i['teams']['away']['id'])
        UTCTime.append(i['date'])
        datetime_est = datetime.strptime(i['date'],'%Y-%m-%dT%H:%M:%S%z') - timedelta(hours=5)
        datetime_est = datetime_est.strftime('%Y-%m-%d')
        ESTTime.append(datetime_est)
    #all_teams = {i['teams']:i['teams'] for i in raw_teams}
    #all_teams = {i['teams']:i['id'] for i in raw_teams}
    games_df = pd.DataFrame({'HomeTeam':homeTeam, 'HomeTeamID':homeTeamID, 'AwayTeam':awayTeam, 'AwayTeamID':awayTeamID, 'UTCDate':UTCTime, 'ESTDate':ESTTime})
    return games_df

#hey = get_all_teams2()
#print(hey)
#print(hey)
#all_games = hey.to_csv("/Users/will.clayton/Desktop/PythonMessAround/BettingHelp/willsbettingapp/all_games.csv")
# In[232]:


def get_all_teams():
    t = [['Anaheim Ducks', 670],
     ['Arizona Coyotes', 1460],
     #['Atlantic Division', 672],
     ['Boston Bruins', 673],
     ['Buffalo Sabres', 674],
     ['Calgary Flames', 675],
     ['Carolina Hurricanes', 676],
     #['Central Division', 677],
     ['Chicago Blackhawks', 678],
     ['Colorado Avalanche', 679],
     ['Columbus Blue Jackets', 680],
     ['Dallas Stars', 681],
     ['Detroit Red Wings', 682],
     ['Edmonton Oilers', 683],
     ['Florida Panthers', 684],
     ['Los Angeles Kings', 685],
     #['Metropolitan Division', 686],
     ['Minnesota Wild', 687],
     ['Montreal Canadiens', 688],
     ['Nashville Predators', 689],
     ['New Jersey Devils', 690],
     ['New York Islanders', 691],
     ['New York Rangers', 692],
     ['Ottawa Senators', 693],
     #['Pacific Division', 694],
     ['Philadelphia Flyers', 695],
     ['Pittsburgh Penguins', 696],
     ['San Jose Sharks', 697],
     ['Seattle Kraken', 1436],
     ['St. Louis Blues', 698],
     ['Tampa Bay Lightning', 699],
     ['Toronto Maple Leafs', 700],
     ['Vancouver Canucks', 701],
     ['Vegas Golden Knights', 702],
     ['Washington Capitals', 703],
     ['Winnipeg Jets', 704]]
    teams = pd.DataFrame(t,columns=['Team','id'])
    return teams

all_games_df = pd.read_csv('all_games.csv')
def get_all_games(date_est):
    all_games_df = pd.read_csv('all_games.csv')
    select_games = all_games_df[all_games_df['ESTDate'] == date_est]
    print(select_games)
    return select_games


# In[234]:


def call_it(teams):
    print('callit used')
    raw_list = []
    for i in teams:
        print("working on team id:",i)
        url = "https://v1.hockey.api-sports.io/games?league=57&season=2022&team={}".format(i)

        payload={}
        headers = {
          'x-rapidapi-key': '96b4e9553b3b604fcf5d4f392bac9c23',
          'x-rapidapi-host': 'v1.hockey.api-sports.io'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        cur_df = get_raw_table(response)
        raw_list.append(cur_df)
        
    return pd.concat(raw_list)


# In[235]:


#get dataframe for a certain team
def get_raw_table(response):
    games = response.json()
    df2 = pd.json_normalize(games,'response')
    df = df2.copy()
    games_columns = ['id','date','teams.away.id','teams.away.name','scores.away','teams.home.id','teams.home.name', 'scores.home', 'status.long']

    df = df[games_columns]
    df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)
    df = df[df['date'] > '2022-10-10']
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    df['HomeResult'] = df.apply(lambda row: math.nan if row['status.long'] == 'Not Started' 
                                else 'W' if row['scores.home']>row['scores.away'] 
                                else 'OTL' if (row['scores.away']>row['scores.home']) & ((row['status.long'] == 'After Over Time') | (row['status.long'] == 'After Penalties'))
                                else 'L', axis=1)

    df['AwayResult'] = df.apply(lambda row: math.nan if row['status.long'] == 'Not Started' 
                                else 'W' if row['scores.home']<row['scores.away'] 
                                else 'OTL' if (row['scores.away']<row['scores.home']) & ((row['status.long'] == 'After Over Time') | (row['status.long'] == 'After Penalties'))
                                else 'L', axis=1)

    df['TotalScore'] = df['scores.home']+df['scores.away']
    #.dt.strftime('%Y-%m-%d')
    #df['day_of_week'] = df['date'].dt.weekday_name
    return df


# In[236]:


# get last 5 home games
def get_last_games(home_team, away_team,df):
    last5home = df[(df['teams.home.id'] == home_team) & (df['status.long'] != 'Not Started') & (df['status.long'] != 'Cancelled')].tail(5)
    last5away = df[(df['teams.away.id'] == away_team) & (df['status.long'] != 'Not Started') & (df['status.long'] != 'Cancelled')].tail(5)
    #last10total = df[((df['teams.home.id'] == team) | (df['teams.away.id'] == team)) & (df['status.long'] != 'Not Started')].tail(5)
    lastH2H = df[((df['teams.home.id'] == home_team) | (df['teams.away.id'] == home_team)) & ((df['teams.home.id'] == away_team) | (df['teams.away.id'] == away_team))]
    return (last5home,last5away,lastH2H)
#display(last10away)
#display(lastH2H)


# In[237]:


def get_record(team,team_df_raw):
    #team_df = team_df[(team_df['teams.home.id'] == team) | (team_df['teams.away.id'] == team)]
    team_df = team_df_raw[team_df_raw['date'] > '2022-10-11']
    wins = len(team_df[(team_df['teams.home.id'] == team) & (team_df['HomeResult'] == 'W')])
    wins += len(team_df[(team_df['teams.away.id'] == team) & (team_df['AwayResult'] == 'W')])
    losses = len(team_df[(team_df['teams.home.id'] == team) & (team_df['HomeResult'] == 'L')])
    losses += len(team_df[(team_df['teams.away.id'] == team) & (team_df['AwayResult'] == 'L')])
    otl = len(team_df[(team_df['teams.home.id'] == team) & (team_df['HomeResult'] == 'OTL')])
    otl += len(team_df[(team_df['teams.away.id'] == team) & (team_df['AwayResult'] == 'OTL')])
    return (wins,losses,otl)




def get_goal_averages(team,df,side, HA='all'):
    #GF
    avg_goals_for_home = df[(df['teams.home.id'] == team)]['scores.home'].mean()
    avg_goals_for_away = df[(df['teams.away.id'] == team)]['scores.away'].mean()

    #GA
    avg_goals_against_home = df[(df['teams.home.id'] == team)]['scores.away'].mean()
    avg_goals_against_away = df[(df['teams.away.id'] == team)]['scores.home'].mean()

    #Both home and away
    goals_for_home = df[(df['teams.home.id'] == team)]['scores.home'].agg(sum)
    goals_for_away = df[(df['teams.away.id'] == team)]['scores.away'].agg(sum)

    goals_against_home = df[(df['teams.home.id'] == team)]['scores.away'].agg(sum)
    goals_against_away = df[(df['teams.away.id'] == team)]['scores.home'].agg(sum)

    home_games = df[(df['teams.home.id'] == team) & (df['scores.home'] != math.nan)]['scores.home'].count()
    away_games = df[(df['teams.away.id'] == team) & (df['scores.away'] != math.nan)]['scores.away'].count()
    total_games = home_games+away_games
    goals_for_total = goals_for_home + goals_for_away
    goals_against_total = goals_against_home + goals_against_away
    avg_goals_for_both = goals_for_total / total_games
    avg_goals_against_both = goals_against_total / total_games
    output = "Average Goals For (Home): \t"+str(round(avg_goals_for_home,2))+          "\nAverage Goals For (Away): \t"+str(round(avg_goals_for_away,2))+         "\nAverage Goals Against (Home): \t"+str(round(avg_goals_against_home,2))+         "\nAverage Goals Against (Away): \t"+str(round(avg_goals_against_away,2))+         "\nAverage Goals For: \t\t"+str(round(avg_goals_for_both,2))+         "\nAverage Goals Against: \t"+str(round(avg_goals_against_both,2))
         
    #print(output)
    #return output
    if HA == 'HA' and side=='home':
        data = {'Average Goals For': [avg_goals_for_home], 
        'Average Goals Against': [avg_goals_against_home],
        'Total Goals': [(avg_goals_for_home+avg_goals_against_home)]
        }
    elif HA == 'HA' and side=='away':
        data = {'Average Goals For': [avg_goals_for_away],
                'Average Goals Against': [avg_goals_against_away],
                'Total Goals': [(avg_goals_for_away+avg_goals_against_away)]
                }
    else:
        data = {'Average Goals For (Home)': [avg_goals_for_home], 
            'Average Goals For (Away)': [avg_goals_for_away],
            'Average Goals Against (Home)': [avg_goals_against_home],
            'Average Goals Against (Away)': [avg_goals_against_away],
            'Average Goals For': [avg_goals_for_both],
            'Average Goals Against': [avg_goals_against_both]
            }
    df = pd.DataFrame(data)

    #return df,output,avg_goals_for_home, avg_goals_for_away, avg_goals_against_home, avg_goals_against_away, avg_goals_for_both, avg_goals_against_both
    return df.T

# In[242]:


def comparison(team1, team2,df,HA='all'):
    awayststs = get_goal_averages(team1,df,'away',HA)

    if HA=='HA':
        avg_gf_side = team1[2]
    else:
        avg_gf_home = (team1[1]+team2[1])/2
        avg_gf_away = (team1[2]+team2[2])/2
        avg_ga_home = (team1[3]+team2[3])/2
        avg_ga_away = (team1[4]+team2[4])/2
        avg_gf_both = (team1[5]+team2[5])/2
        avg_ga_both = (team1[6]+team2[6])/2
        avg_total = avg_gf_both + avg_ga_both
    
    output = "Average Goals For (Home): \t"+str(round(avg_gf_home,2))+          "\nAverage Goals For (Away): \t"+str(round(avg_gf_away,2))+         "\nAverage Goals Against (Home): \t"+str(round(avg_ga_home,2))+         "\nAverage Goals Against (Away): \t"+str(round(avg_ga_away,2))+         "\nAverage Goals For: \t\t"+str(round(avg_gf_both,2))+         "\nAverage Goals Against: \t"+str(round(avg_ga_both,2))+     "\nAverage Goals Total: \t\t"+str(round(avg_total,2))
    
    return output,avg_gf_home,avg_gf_away,avg_ga_home,avg_ga_away,avg_gf_both,avg_ga_both,avg_total
    return df.T
#team1 = get_goal_averages(670,master)
#team2 = get_goal_averages(1460,master)
#print(comparison(team1, team2)[0])
#test2 = call_it([670,675])
#test2.to_csv('/Users/will.clayton/Desktop/dummyframe.csv')

def record_text(record):
    return str(record[0])+"-"+str(record[1])+"-"+str(record[2])


def create_table(at, ht, HA='all'):
    # code to retrieve selected options from dropdown menus and update label text
    teams = get_all_teams()
    hometeam = teams[teams['Team'] == ht]['id'].iloc[0]
    awayteam = teams[teams['Team'] == at]['id'].iloc[0]
    teams = [hometeam,awayteam]
    master = call_it(teams)
    #master = pd.read_csv('dummyframe.csv')
    #home_record = get_record_text(get_record(hometeam,master))
    #text = home_record
    home_text = get_goal_averages(hometeam,master,'home',HA)
    print("home",home_text)

    #home_team_label.config(text=text)
    #home_team_label.update()
    
    #away_record = get_record_text(get_record(awayteam,master))
    #text2 = away_record
    away_text = get_goal_averages(awayteam,master,'away',HA)
    
    #get record here
    results = get_last_games(hometeam,awayteam,master)
    home_record = get_record(hometeam,master)
    away_record = get_record(awayteam,master)

    home_home_record = get_record(hometeam,master[master['teams.home.name'] == ht])
    away_away_record = get_record(awayteam,master[master['teams.away.name'] == at])
    return home_text,away_text,results,home_record,away_record,home_home_record,away_away_record
def getL5text(df,HA):
    output = ''
    record = ''
    res = []
    result = ''
    df = df.sort_values(by='date',ascending=False)
    df = df[df['status.long'] != 'Not Started']
    print(df)
    print(df.groupby(['HomeResult'])['HomeResult'].count())
    if HA == 'h':
        for index, row in df.iterrows():
            res.append(row['HomeResult'])
            output += ( '{:<3s} {}-{}  @ {:<22s} | {} \n'.format(row['HomeResult'],str(int(row['scores.home'])),str(int(row['scores.away'])), row['teams.away.name'], row['date'][5:]) )
    elif HA == 'a': 
        for index, row in df.iterrows():
            res.append(row['AwayResult'])
            output += ( '{:<3s} {}-{}  @ {:<22s} | {} \n'.format(row['AwayResult'],str(int(row['scores.away'])),str(int(row['scores.home'])), row['teams.home.name'], row['date'][5:]) )
    elif HA == 'h2h':
        df = df.drop_duplicates(subset=['id'])
        print(df)
        for index, row in df.iterrows():
            output += ( '{:<22s} {} | {} {:<22s} | {}\n'.format(row['teams.away.name'],str(int(row['scores.away'])),str(int(row['scores.home'])), row['teams.home.name'], row['date'][5:]) )
            #output += row['teams.away.name']+" "+str(int(row['scores.away']))+" | "+str(int(row['scores.home']))+" "+row['teams.home.name']+"\t| "+row['date'][5:] +"\n"
    result = str(res.count('W'))+"-"+str(res.count('L'))+"-"+str(res.count('OTL'))
    print(result)
    return output,result

def app():
    st.set_page_config(page_title="Dropdown Example", page_icon=":guardsman:", layout="wide")
    topl, topm,topr = st.columns(3)
    gameday = topl. date_input ( 'Date Selection' , value=None , min_value=None , max_value=None , key=None )
    topr.empty()
    #topr.text(get_all_games(str(gameday)))
    
    

    numgames = (str(get_all_games(str(gameday))['HomeTeam'].count())+" Games on "+str(gameday))
    awayTeamdate = get_all_games(str(gameday))['AwayTeam']
    homeTeamdate = get_all_games(str(gameday))['HomeTeam']
    matchup = topm.selectbox(numgames, awayTeamdate+" @ "+homeTeamdate)
    left_side, middle, right_side = st.columns(3)
    left_side.header('Away Team')
    middle.header('Home Team')
    
    right_side.header('Comparison')
    match_check = topr.checkbox("Use Matchup")
    if match_check:
        option1 = left_side.selectbox("Away Team", [matchup.split(' @ ')[0]])
        option2 = middle.selectbox("Home Team", [matchup.split(' @ ')[1]])
    else:
        option1 = left_side.selectbox("Away Team", get_all_teams())
        option2 = middle.selectbox("Home Team", get_all_teams())
    
    checkbox = topr.checkbox("Only Home/Away Stats")
    
    #far_right.empty()
    if topr.button("See Results"):
        right_side.text('')    
        right_side.text('')    
        right_side.text('')    
        right_side.text('')     
        if checkbox:
            table = create_table(option1, option2,'HA')
            left_col = str(option1)+' Away Stats'
            middle_col = str(option2)+' Home Stats'
        else:
            table = create_table(option1, option2)
            left_col = str(option1)+' - All Stats'
            middle_col = str(option2)+' - All Stats'
        
        middle.text("Overall Record: "+record_text(table[3])+"\t("+str(round(table[3][0]/(table[3][0]+table[3][1]+table[3][2]),3))+")")
        middle.text("Home Record: "+record_text(table[5]))

        left_side.text("Overall Record: "+record_text(table[4])+"\t("+str(round(table[4][0]/(table[4][0]+table[4][1]+table[4][2]),3))+")")
        left_side.text("Away Record: "+record_text(table[6]))
        
        table[1].columns = [left_col]
        left_side.dataframe(table[1], width=600)



        
        table[0].columns = [middle_col]
        middle.dataframe(table[0], width=600)
        
        c = pd.concat([table[0],table[1]],axis=1,ignore_index=True)
        c.columns = [left_col,middle_col]
        c2 = pd.DataFrame(c)
        #c=c.rename(columns={0:[option1],1:[option2]})
        #c['Totals'] = c[option1]+c[option2]
        right_side.dataframe(c, width=600)

        left_side.text("Last 5 Away Games ("+getL5text(table[2][1],'a')[1]+")")
        left_side.text(getL5text(table[2][1],'a')[0])

        middle.text("Last 5 Home Games ("+getL5text(table[2][0],'h')[1]+")")
        middle.text(getL5text(table[2][0],'h')[0])

        right_side.text("Previous Matchups\n")
        right_side.text(getL5text(table[2][2],'h2h')[0])

        #getting record
        print(table[3])
        

    right_side.text('')    
    right_side.text('')    
    right_side.text('')   
if __name__ == '__main__':
    app()