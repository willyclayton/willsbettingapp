import pandas as pd
import requests
import math
import streamlit as st
#hello there
#this is another update?
print('do something now hahaha')



def get_all_teams2():
    url = "https://v1.hockey.api-sports.io/teams?league=57&season=2022"

    payload={}
    headers = {
      'x-rapidapi-key': '96b4e9553b3b604fcf5d4f392bac9c23',
      'x-rapidapi-host': 'v1.hockey.api-sports.io'
    }

    teams = requests.request("GET", url, headers=headers, data=payload)

    raw_teams = teams.json()
    raw_teams = raw_teams['response']
    all_teams = {i['name']:i['id'] for i in raw_teams}
    teamdf = pd.DataFrame(all_teams.items(),columns=['Team','id'])
    return teamdf


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


# In[233]:


teams = get_all_teams()


# In[234]:


def call_it(teams):
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
def get_last_games():
    last5home = df[(df['teams.home.id'] == 670) & (df['status.long'] != 'Not Started')].tail(5)
    last5away = df[(df['teams.away.id'] == 670) & (df['status.long'] != 'Not Started')].tail(5)
    last10total = df[((df['teams.home.id'] == 670) | (df['teams.away.id'] == 670)) & (df['status.long'] != 'Not Started')].tail(5)
    lastH2H = df[((df['teams.home.id'] == 670) | (df['teams.away.id'] == 670)) & ((df['teams.home.id'] == 673) | (df['teams.away.id'] == 673))]

#display(last10away)
#display(lastH2H)


# In[237]:


def get_record(team,team_df):
    #team_df = team_df[(team_df['teams.home.id'] == team) | (team_df['teams.away.id'] == team)]
    wins = len(team_df[(team_df['teams.home.id'] == team) & (team_df['HomeResult'] == 'W')])
    wins += len(team_df[(team_df['teams.away.id'] == team) & (team_df['AwayResult'] == 'W')])
    losses = len(team_df[(team_df['teams.home.id'] == team) & (team_df['HomeResult'] == 'L')])
    losses += len(team_df[(team_df['teams.away.id'] == team) & (team_df['AwayResult'] == 'L')])
    otl = len(team_df[(team_df['teams.home.id'] == team) & (team_df['HomeResult'] == 'OTL')])
    otl += len(team_df[(team_df['teams.away.id'] == team) & (team_df['AwayResult'] == 'OTL')])
    return (wins,losses,otl)


# In[238]:


def get_record_text(raw):
    text = "__Record__\n"+str(raw[0])+"-"+str(raw[1])+"-"+str(raw[2])+"\n\n"
    return text


# In[239]:


#print(get_record_text(get_record(670,master)))




#master = call_it([670,682])


# In[241]:


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

def create_table(at, ht, HA='all'):
    # code to retrieve selected options from dropdown menus and update label text
    teams = get_all_teams()
    hometeam = teams[teams['Team'] == ht]['id'].iloc[0]
    awayteam = teams[teams['Team'] == at]['id'].iloc[0]
    teams = [hometeam,awayteam]
    master = call_it(teams)
    
    home_record = get_record_text(get_record(hometeam,master))
    text = home_record
    text = get_goal_averages(hometeam,master,'home',HA)
    #home_team_label.config(text=text)
    #home_team_label.update()
    
    away_record = get_record_text(get_record(awayteam,master))
    text2 = away_record
    text2 = get_goal_averages(awayteam,master,'away',HA)
    #away_team_label.config(text=text2)
    #away_team_label.update()
     
    team1 = get_goal_averages(hometeam,master,'home')
    team2 = get_goal_averages(awayteam,master,'away')
    
    text3 = "Comparison\n"
    #text3 = comparison(team1, team2)
    #comparison_label.config(text=text3)
    #comparison_label.update()
    return text,text2

def app():
    st.set_page_config(page_title="Dropdown Example", page_icon=":guardsman:", layout="wide")

    left_side, middle, right_side = st.columns(3)
    left_side.header('Away Team Side')
    middle.header('Home Team Side')
    
    right_side.header('Comparison')

    option1 = left_side.selectbox("Away Team", get_all_teams())
    option2 = middle.selectbox("Home Team", get_all_teams())
    
    checkbox = right_side.checkbox("Only Home/Away Stats")
    #far_right.empty()
    if right_side.button("See Results"):
        if checkbox:
            table = create_table(option1, option2,'HA')
            left_col = str(option1)+' Away Stats'
            middle_col = str(option2)+' Home Stats'
        else:
            table = create_table(option1, option2)
            left_col = str(option1)+' - All Stats'
            middle_col = str(option2)+' - All Stats'
        
        left_side_df = pd.DataFrame(table[0],columns=[option1])
        
        table[0].columns = [left_col]
        left_side.dataframe(table[0], width=600)

        right_side_df = pd.DataFrame(table[1],columns=[option2])

        
        table[1].columns = [middle_col]
        middle.dataframe(table[1], width=600)
        
        c = pd.concat([table[0],table[1]],axis=1,ignore_index=True)
        c.columns = [left_col,middle_col]
        c2 = pd.DataFrame(c)
        #c=c.rename(columns={0:[option1],1:[option2]})
        #c['Totals'] = c[option1]+c[option2]
        right_side.dataframe(c, width=600)
    
    right_side.text('')    
    right_side.text('')    
    right_side.text('')    


if __name__ == '__main__':
    app()