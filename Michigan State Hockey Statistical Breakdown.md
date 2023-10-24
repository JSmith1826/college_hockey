### TEMP - DB Scructure to remind GPT

Database Structure Summary
1. game_details
Day
Date
Conference
Details
Location
Ref1
Ref2
Asst_Ref1
Asst_Ref2
Attendance
Game_ID

2. scoring_summary
Period
Team
PP (Power Play)
Player
Player_Goals
Assist1
Assist2
Time
(and more...)

3. penalty_summary
Period
Team
Player
Pen_Length
Penalty_Type
Time
Game_ID


4. goalie_stats
Team
Goalie
SV (Saves)
GA (Goals Against)
Minutes
Game_ID


5. player_stats
Team
Player
G (Goals)
A (Assists)
Pt. (Points)
+/-
Sh (Shots)
PIM (Penalty Minutes)
FOW (Face-offs Won)
FOL (Face-offs Lost)
FO% (Face-off Percentage)
Game_ID

6. line_chart
Team
Line
Position
Player
Game_ID

7. linescore
Team
goals1, goals2, goals3, goalsT (Goals by period and total)
shots1, shots2, shots3, shotsT (Shots by period and total)
Pen (Penalties)
PIM (Penalty Minutes)
PPG (Power Play Goals)
PPO (Power Play Opportunities)
FOW (Face-offs Won)
FOL (Face-offs Lost)
FOW% (Face-off Percentage)
Game_ID


8. advanced_metrics_team1
Player
Metrics like TOTAL_Block, TOTAL_Miss, TOTAL_Saved, TOTAL_Goals, etc.
Game_ID

9. advanced_metrics_team2
Similar to advanced_metrics_team1


## CSV Structure Summary (2023_master_roster.csv)
Unnamed: 0
No. (Jersey Number)
Name
Yr. (Year/Class)
Ht. (Height)
Wt. (Weight)
DOB (Date of Birth)
Hometown
Position
Height_Inches
Draft_Year
NHL_Team
D_Round (Draft Round)
Last Team
League
School