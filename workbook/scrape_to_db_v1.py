import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import json

from sqlalchemy import create_engine
import sqlite3


## This book parses a box score from collegehockeynews.com ans well as the advanced metrics from the same game
# The seperate elements of the game box score are stored in a list of dataframes
# the dataframes are then stored in a dictionary and output as a json file

# Example box score link
url_box = 'https://www.collegehockeynews.com/box/final/20230211/mic/msu/'

# Example metrics link from same game
url_metrics = 'https://www.collegehockeynews.com/box/metrics.php?gd=96398'

box_score_url = 'https://www.collegehockeynews.com/box/final/20230211/mic/msu/'
advanced_metrics_url = 'https://www.collegehockeynews.com/box/metrics.php?gd=96211'

############# PARSEING SCORING SUMMARY WITH BS4


def parse_scoring_summary(html_content):
    # Initialize BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the scoring div and table
    scoring_div = soup.find('div', id='scoring')
    if scoring_div is None:
        return "Scoring div not found"

    scoring_table = scoring_div.find('table')
    if scoring_table is None:
        return "Scoring table not found"

    # Initialize list to store scoring events
    scoring_events = []
    period = None

    # Loop through table rows
    for row in scoring_table.find_all('tr'):
        if 'stats-section' in row.get('class', []):
            period = row.find('td').text.strip()
        else:
            cols = row.find_all('td')
            if len(cols) > 1:
                team = cols[0].text.strip()
                pp = cols[1].text.strip()

                player_data = cols[3].text.strip()
                match = re.match(r"(.+)\s\((\d+)\)", player_data)
                if match:
                    player = match.group(1)
                    goals = int(match.group(2))
                else:
                    player = player_data
                    goals = None

                assist_data = cols[4].text.strip().split(", ")
                assist1 = assist_data[0] if len(assist_data) > 0 else None
                assist2 = assist_data[1] if len(assist_data) > 1 else None

                time = cols[5].text.strip()

                scoring_event = {
                    'Period': period,
                    'Team': team,
                    'PP': pp,
                    'Player': player,
                    'Player_Goals': goals,
                    'Assist1': assist1,
                    'Assist2': assist2,
                    'Time': time
                }
                scoring_events.append(scoring_event)

    return pd.DataFrame(scoring_events)

# # Parse the scoring summary and convert it to a DataFrame
# scoring_summary = parse_scoring_summary(html_content)
# df = pd.DataFrame(scoring_summary)
# print(df)


####### Parse Penalty Summary WITH BS4 #######
def parse_penalty_summary(html_content):
    # Initialize BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the penalties div and table (assuming the structure is similar to the scoring section)
    penalties_div = soup.find('div', id='penalties')
    if penalties_div is None:
        return "Penalties div not found"

    penalties_table = penalties_div.find('table')
    if penalties_table is None:
        return "Penalties table not found"

    # Initialize list to store penalty events
    penalty_events = []
    period = None
    
    # Loop through table rows
    for row in penalties_table.find_all('tr'):
        if 'stats-section' in row.get('class', []):
            period = row.find('td').text.strip()
        else:
            cols = row.find_all('td')
            if len(cols) > 1:
                team = cols[0].text.strip()
                player = cols[1].text.strip()
                pen_length = cols[2].text.strip()
                penalty_type = cols[3].text.strip()
                time = cols[4].text.strip()

                penalty_event = {
                    'Period': period,
                    'Team': team,
                    'Player': player,
                    'Pen_Length': pen_length,
                    'Penalty_Type': penalty_type,
                    'Time': time
                }
                penalty_events.append(penalty_event)

    return pd.DataFrame(penalty_events)

# # Use the function and convert the result to a DataFrame
# penalty_summary = parse_penalty_summary(html_content)
# df_penalties = pd.DataFrame(penalty_summary)
# # print(df_penalties)

def parse_goalie_stats(html_content):
    # Initialize BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the goalies div and table
    goalies_div = soup.find('div', id='goalies')
    if goalies_div is None:
        return "Goalies div not found"

    goalies_table = goalies_div.find('table')
    if goalies_table is None:
        return "Goalies table not found"

    # Initialize list to store goalie stats
    goalie_stats = []
    team = None

    # Loop through table rows
    for row in goalies_table.find_all('tr'):
        if 'stats-header' in row.get('class', []):
            team = row.find('td').text.strip()
        else:
            cols = row.find_all('td')
            if len(cols) > 1:
                goalie = cols[0].text.strip()
                sv = cols[1].text.strip()
                ga = cols[2].text.strip()
                minutes = cols[3].text.strip()

                goalie_stat = {
                    'Team': team,
                    'Goalie': goalie,
                    'SV': sv,
                    'GA': ga,
                    'Minutes': minutes
                }
                goalie_stats.append(goalie_stat)

    return pd.DataFrame(goalie_stats)

# # Use the function and convert the result to a DataFrame
# goalie_stats_data = parse_goalie_stats(html_content)
# df_goalie_stats = pd.DataFrame(goalie_stats_data)
# print(df_goalie_stats)



#### PARSE PLAYER STATS TABLE ####
def parse_player_summary(html_content):
    # Initialize BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the playersums div
    playersums_div = soup.find('div', id='playersums')
    if playersums_div is None:
        return "Player summaries div not found"

    # Initialize list to store player stats
    player_stats = []

    # Loop through each playersum div
    for player_sum in playersums_div.find_all('div', class_='playersum'):
        team = player_sum.find('td').text.strip()
        
        # Loop through table rows
        for row in player_sum.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 1:
                player = cols[0].text.strip()
                goals = cols[1].text.strip()
                assists = cols[2].text.strip()
                points = cols[3].text.strip()
                plus_minus = cols[4].text.strip()
                shots = cols[5].text.strip()
                pim = cols[6].text.strip()
                fowl = cols[7].text.strip() if len(cols) > 7 else None
                
                fow, fol = None, None
                win_percentage = None
                
                

                try:
                    if fowl and '‑' in fowl:  # Checking if it contains a hyphen
                        fow, fol = map(int, fowl.split('‑'))
                        total_fo = fow + fol
                        win_percentage = (fow / total_fo) * 100 if total_fo > 0 else 0
                except ValueError:
                    fow, fol, win_percentage = None, None, None

                

                
                player_stat = {
                    'Team': team,
                    'Player': player,
                    'G': goals,
                    'A': assists,
                    'Pt.': points,
                    '+/-': plus_minus,
                    'Sh': shots,
                    'PIM': pim,
                    'FOW': fow,
                    'FOL': fol,
                    'FO%': win_percentage
                }
                player_stats.append(player_stat)

    return pd.DataFrame(player_stats)

# # Use the function and convert the result to a DataFrame
# player_stats_data = parse_player_summary(html_content)
# df_player_stats = pd.DataFrame(player_stats_data)
# # print(df_player_stats)


from bs4 import BeautifulSoup
import pandas as pd

def parse_advanced_metrics_tables(html_content):
    # Initialize list to store DataFrames
    dfs = []
    
    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table', {'class': 'sortable metrics'})
    
    for table in tables:
        # Initialize list to store column names and data
        col_names = []
        col_names_final = []
        data = []
        
        # Get headers
        headers = table.find_all('th')
        for header in headers:
            col_names.append(header.text)
        
        # Add TOTAL, EVEN STRENGTH, POWER PLAY, CLOSE to column names
        section_headers = ['TOTAL', 'EVEN STRENGTH', 'POWER PLAY', 'CLOSE']
        for col in col_names:
            for section in section_headers:
                if col in section_headers:
                    temp_col = section
                else:
                    temp_col = f"{section}_{col}"
            col_names_final.append(temp_col)
        
        print(f"Length of final column names: {len(col_names_final)}")  # Debug statement
        
        # Get data rows
        rows = table.find_all('tr')[2:]  # skip header rows
        for row in rows:
            row_data = []
            cells = row.find_all('td')
            for cell in cells:
                row_data.append(cell.text.strip())
            data.append(row_data)
        
        print(f"Length of first row of data: {len(data[0])}")  # Debug statement
        
        # Create DataFrame and append to list
        df = pd.DataFrame(data, columns=col_names_final)
        dfs.append(df)
    
    return dfs

# Placeholder for your actual HTML content
# html_metrics_sample = '''...'''  # Replace with actual HTML content

# Get the HTML content
# url_metrics = 'https://www.collegehockeynews.com/box/metrics.php?gd=96211'  # Replace this with your URL
# response = requests.get(url_metrics)
# html_metrics_sample = response.text

# # Parse and convert to DataFrames
# # This will return a list of DataFrames, one for each team
# # dfs[0] will be the DataFrame for the first team, dfs[1] for the second team
# dfs = parse_advanced_metrics_tables(html_metrics_sample)

# # To check the DataFrame for the first team
# dfs[0].head()
# dfs[1].head()

# Complete code for parsing the line chart information with specific positions for forwards and defensemen.


def parse_line_chart(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    line_chart_div = soup.find('div', id='linechart')

    line_data = []

    for team_div in line_chart_div.find_all('div', recursive=False):
        team_name = team_div.find('h3').text.strip()
        for line_type_div in team_div.find_all('div', recursive=False):
            line_type = line_type_div.get('class')[0]
            if line_type == 'f':
                position_types = ['Left Wing', 'Center', 'Right Wing']
            elif line_type == 'd':
                position_types = ['Left D', 'Right D']
            elif line_type == 'x':
                position_types = ['Extra']
            elif line_type == 'g':
                position_types = ['Goalie']
                goalie_count = 1  # Initialize goalie count
            else:
                continue

            players = line_type_div.find_all('div')
            for i, player in enumerate(players):
                player_name = player.text.strip()
                # Remove (F) or (D) from extras
                if line_type == 'x':
                    player_name = player_name.split(' ')[0]
                # Assign a line to goalies
                if line_type == 'g':
                    line_number = f"Goalie {goalie_count}"
                    goalie_count += 1  # Increment goalie count
                else:
                    line_number = i // len(position_types) + 1

                position = position_types[i % len(position_types)]
                line_data.append({
                    'Team': team_name,
                    'Line': line_number,
                    'Position': position,
                    'Player': player_name
                })

    return pd.DataFrame(line_data)


# # Use the function and convert the result to a DataFrame
# line_chart_data = parse_line_chart(html_content)
# df_line_chart = pd.DataFrame(line_chart_data)
# df_line_chart

### Get the Linescore Elements - Score, shots, ect by period####

def parse_linescore(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    linescore_data = []
    
    # Parsing the Goals table
    goals_table = soup.select_one("#goals table")
    rows = goals_table.select('tbody tr')
    for row in rows:
        team_data = {}
        team_data['Team'] = row.select_one('td').text
        goals = row.select('td')[1:]
        for i, goal in enumerate(goals):
            team_data[f'goals{i+1}' if i < len(goals) - 1 else 'goalsT'] = int(goal.text)
        
        linescore_data.append(team_data)
    
    # Parsing the Shots table
    shots_table = soup.select_one("#shots table")
    rows = shots_table.select('tbody tr')
    for i, row in enumerate(rows):
        shots = row.select('td')[1:]
        for j, shot in enumerate(shots):
            linescore_data[i][f'shots{j+1}' if j < len(shots) - 1 else 'shotsT'] = int(shot.text.strip())
    
    # Parsing the PP table
    pp_table = soup.select_one("#pp table")
    rows = pp_table.select('tbody tr')
    for i, row in enumerate(rows):
        pen_pim = row.select('td')[1].text.split('‑')
        linescore_data[i]['Pen'] = int(pen_pim[0])
        linescore_data[i]['PIM'] = int(pen_pim[1])
        
        ppg_ppo = row.select('td')[2].text.split('‑')
        linescore_data[i]['PPG'] = int(ppg_ppo[0])
        linescore_data[i]['PPO'] = int(ppg_ppo[1])
        
        fow_fol = row.select('td')[3].text.split('‑')
        linescore_data[i]['FOW'] = int(fow_fol[0])
        linescore_data[i]['FOL'] = int(fow_fol[1])
        linescore_data[i]['FOW%'] = (linescore_data[i]['FOW'] / (linescore_data[i]['FOW'] + linescore_data[i]['FOL'])) * 100
        
    return pd.DataFrame(linescore_data)



# # Use the function and get the DataFrame
# df_linescore = parse_linescore(html_content)
# df_linescore




# Function to parse game details

from bs4 import BeautifulSoup
import re
import pandas as pd

def parse_game_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    meta_div = soup.find('div', {'id': 'meta'})
    game_details_div = meta_div.find_all('div')[-1]
    
    date_str = game_details_div.h4.string
    day_of_week, date = date_str.split(", ", 1)
    
    p_elements = game_details_div.find_all('p')
    details_strs = p_elements[0].get_text(separator='|').split('|')
    
    conference = details_strs[0]
    location = details_strs[-1].split('at ')[-1]
    details = details_strs[1] if len(details_strs) > 2 else None
    
    refs_str = p_elements[1].strong.next_sibling
    asst_refs_str = p_elements[1].find_all('strong')[1].next_sibling
    attendance_str = p_elements[1].find_all('strong')[2].next_sibling
    
    refs = refs_str.split(', ')
    asst_refs = asst_refs_str.split(', ')
    refs = [re.sub(r'[^a-zA-Z ]+', '', ref).strip() for ref in refs]
    asst_refs = [re.sub(r'[^a-zA-Z ]+', '', ref).strip() for ref in asst_refs]
    
    attendance = attendance_str.split(": ")[-1]
    attendance = int(attendance.replace(',', ''))
    
    details = details.replace('\n', '').strip()
    details = re.sub('\t', ' ', details)
    
    game_details = {
        'Day': day_of_week,
        'Date': date,
        'Conference': conference,
        'Details': details,
        'Location': location,
        'Ref1': refs[0],
        'Ref2': refs[1] if len(refs) > 1 else None,
        'Asst_Ref1': asst_refs[0],
        'Asst_Ref2': asst_refs[1] if len(asst_refs) > 1 else None,
        'Attendance': attendance
    }
    
    game_details_df = pd.DataFrame([game_details])
    return game_details_df


# # Test the function
# game_details_df = parse_game_details(html_content)
# game_details_df

def parse_box_score(box_score_html):
    # Parse box score into DataFrames
    
    scoring_summary = parse_scoring_summary(box_score_html)
    penalty_summary = parse_penalty_summary(box_score_html)
    goalie_stats = parse_goalie_stats(box_score_html)
    player_stats = parse_player_summary(box_score_html)
    line_chart = parse_line_chart(box_score_html)
    linescore = parse_linescore(box_score_html)
    game_details = parse_game_details(box_score_html)

    
    
    # Combine DataFrames into a list
    all_dfs = [game_details, scoring_summary, penalty_summary, goalie_stats, player_stats, line_chart, linescore]
    

    
    return all_dfs

def rename_duplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in df.columns[df.columns.duplicated()].unique(): 
        cols[df.columns.get_loc(dup)] = [f"{dup}_{i}" if i != 0 else dup for i in range(df.columns.get_loc(dup).sum())]
    df.columns = cols
    return df




# Function to save DataFrames to SQLite database
def save_to_sqlite_db(df_list, table_names, db_name='test_hockey_data.db'):
    engine = create_engine(f'sqlite:///{db_name}')
    
    for df, table in zip(df_list, table_names):
        # Rename duplicate columns
        df = rename_duplicate_columns(df)
        df.to_sql(table, engine, if_exists='replace')

# Function to fetch and save data
def fetch_and_save_data_to_db(box_score_url, advanced_metrics_url, db_name='hockey_data.db'):
    # Fetch HTML content for box score
    box_score_response = requests.get(box_score_url)
    box_score_html = box_score_response.text
    
    # Fetch HTML content for advanced metrics
    advanced_metrics_response = requests.get(advanced_metrics_url)
    advanced_metrics_html = advanced_metrics_response.text
    
    # Parse box score into list of DataFrames
    box_score_dfs = parse_box_score(box_score_html)
    
    # Parse advanced metrics into list of DataFrames
    advanced_metrics_dfs = parse_advanced_metrics_tables(advanced_metrics_html)
    
    # Combine all DataFrames into a list
    all_dfs = box_score_dfs + advanced_metrics_dfs
    
    # Define table names for these DataFrames
    table_names = ['scoring_summary', 'penalty_summary', 'goalie_stats', 'player_stats', 'line_chart', 'linescore',
                   'advanced_metrics_team1', 'advanced_metrics_team2']
    # for df in all_dfs:
    #     # print(type(df))
    #     print(df.columns.tolist())

    
    # Save DataFrames to SQLite database
    save_to_sqlite_db(all_dfs, table_names, db_name)
    
    return all_dfs

# # Replace with actual URLs
# base_url = 'https://www.collegehockeynews.com'
# box_score_url = 'https://www.collegehockeynews.com/box/final/20230211/mic/msu/'
# advanced_metrics_url = 'https://www.collegehockeynews.com/box/metrics.php?gd=96211'

# Fetch, parse, and save data
all_dfs = fetch_and_save_data_to_db(box_score_url, advanced_metrics_url)



