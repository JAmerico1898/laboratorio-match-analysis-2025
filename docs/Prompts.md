## # Variáveis 

## # 2 

## High Recoveries % 

Recoveries refer to the number of times a team regains possession of the ball after losing it. This can include various scenarios such as intercepting passes, winning duels, or collecting loose balls. High Recoveries Refers to the percentage of recoveries that take place in the attacking third of the pitch. 

## Context: 

You are a soccer analytics specialist. High Recoveries (%) refer to the number of times a team regains possession of the ball after losing it. This can include various scenarios such as intercepting passes, winning duels, or collecting loose balls. High Recoveries Refers to the percentage of recoveries that take place in the attacking third of the pitch, or "start_x">=66.7. The attached code calculates Recoveries (total) 

## Task: 

Adjust the code below so that you calculate High Recoveries then divide it by Recoveries to get High Recoveries (%). 

## # 4 

## # Fouls in attacking half % 

"""Represents an important tactical metric that quantifies a team's approach to disrupting opposition counter-attacks in advanced areas of the pitch. This metric can be precisely defined as: The percentage of a team's total fouls that occur in the opponent's half of the pitch during defensive transition situations: Calculated as: (Number of fouls committed in the attacking half during transitions ÷ Total fouls committed during transitions) × 100 

""" 

## Context: 

Fouls in attacking half (%) is the percentage of a team's total fouls that occur in the opponent's half of the pitch during defensive transition situations: Calculated as: (Number of fouls committed in the attacking half during transitions ÷ Total fouls committed during transitions) × 100. progcarry_df2 dataframe identifies possession chains during football matches. “possessionId” numbers possession chains for each “team_id” (1, 2, 3…) independently. “first_chain”==1 marks the beginning of a chain, while “last_chain”==1 mark the ending of it. Fouls are identified as "type_id" == 4 & “outcome”==0. The attacking half is defined by “x_start”>=50. 

## Task: 

Write a Python code so that for each “game_id” and “team_id”, it calculates “fouls in attacking half (%)” 

## # Variáveis 

# 7 

## # Counter-Press Success Rate % 

""" 

This metric is defined as the percentage of counter-pressing sequences that successfully result in the team regaining possession within 5 seconds after losing the ball. Evaluates the effectiveness of a team's immediate pressing actions after losing possession. It is calculated as: (Number of successful counter-presses ÷ Total counter-press attempts) × 100 

""" 

Variável 11 de MatchAnalysis. **RESOLVIDO** 

# Variáveis 

# 8 

## # Transition Vulnerability Index 

"""Ratio of opposition progressive passes completed in first 10 seconds after possession loss. quantifies a team's susceptibility to opposition counter-attacks following possession loss.""" 

## ###CALCULATE 

### progcarry_df2 has progressive passes dummy 

## Context: 

You are a soccer analytics specialist. “Transition Vulnerability Index” is the ratio of opposition progressive passes completed in first 8 seconds after possession loss. quantifies a team's susceptibility to opposition counter-attacks following possession loss. progcarry_df2 dataframe "progressive_pass" is a dummy that assigns 1 if the pass is progressive and 0 otherwise. progcarry_df2 dataframe also identifies possession chains during football matches. “possessionId” numbers possession chains for each “team_id” (1, 2, 3…) independently. “first_chain”==1 marks the beginning of a chain, while “last_chain”==1 mark the ending of it. progcarry_df2[“time”] records the continued time of the game in seconds. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Transition Vulnerability Index” as the ratio of progressive passes ("progressive_pass"==1) and total passes (“type_id==1”) in up to 8 seconds after the other “team_id” loses possession “last_chain”==1. 

# Variáveis 

## # ATTACKING TRANSITION 

# 11 

#Time to progression after own half recovery (s) 

"""The average time (in seconds) between regaining possession in one's own half and successfully progressing the ball into the opponent's half or a more advanced attacking position. It specifically focuses on transitions initiated in the defensive half, emphasizing a team's ability to move from defense to attack quickly.""" 

## Context: 

You are a soccer analytics specialist. “Time to progression after own half recovery (s)” is the average time (in seconds) between regaining possession in one's own half and successfully progressing the ball into the opponent's half. progcarry_df2 dataframe progcarry_df2 dataframe identifies possession chains during football matches. “possessionId” numbers possession chains for each “team_id” (1, 2, 3…) independently. “first_chain”==1 marks the beginning of a chain, while “last_chain”==1 marks the ending of it. progcarry_df2[“time”] records the continued time of the game in seconds. Own half of the field is start_x <50 and opponent’s half is start_x>=50. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Time to progression after own half recovery (s)”. 

## # Variáveis 

## # 12 

#First pass forward % 

"""Quantifies a team's immediate intent to progress play after regaining possession. The percentage of possession recoveries where the very first pass made by the team is played in a forward direction. Calculated as: (Number of forward first passes after recovery ÷ Total number of recoveries with a pass) × 100""" 

## Context: 

You are a soccer analytics specialist. “First pass forward %” is percentage of possession recoveries where the very first pass made by the team is played in a forward direction. It is Calculated as: (Number of forward first passes after recovery ÷ Total number of recoveries with a pass) × 100. progcarry_df2 dataframe identifies possession chains during football matches. “possessionId” numbers possession chains for each “team_id” (1, 2, 3…) independently. “first_chain”==1 marks the beginning of a chain, while “last_chain”==1 marks the ending of it. “start_x” defines the initial x coordinate of a given event, while “end_x” defines its final coordinate. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “First pass forward %”. 

# Variáveis 

# 13 

#Final third entries within 10s after own half recovery % 

"""Final third entries within 10s after recovery refers to the number of times a team successfully moves the ball into the final third of the pitch within 10 seconds after regaining possession IN ITS OWN HALF. This metric helps in understanding the effectiveness and speed of a team's transition from defense to attack. It indicates how quickly a team can create potential scoring opportunities after recovering the ball.""" 

## Context: 

You are a soccer analytics specialist. “Final third entries within 10s after own half recovery %” refers to the number of times a team successfully moves the ball into the final third of the pitch within 10 seconds after regaining possession IN ITS OWN HALF. “x_start” < 50 defines own half. 

## Task: 

The code below calculates Final third entries within 10s after recovery. Therefore, it must be adjusted so that the valid_recoveries variable includes own half condition. progcarry_df2 dataframe identifies possession chains during football matches. “possessionId” numbers possession chains for each “team_id” (1, 2, 3…) independently. “first_chain”==1 marks the beginning of a chain, while “last_chain”==1 marks the ending of it. “start_x” defines the initial x coordinate of a given event, while “end_x” defines its final coordinate. 

# Variáveis 

# 17 

## # Buildup from goalkick % 

"""Quantifies a team's approach to initiating possession from goal kicks and their effectiveness in establishing controlled possession from these situations. Calculated as the percentage of goal kicks that successfully lead to established possession beyond the initial receiving phase. Established possession is at least 8 sec, 3 passes and 4 different players. """ 

## Context: 

You are a soccer analytics specialist. “Buildup from goalkick %” quantifies a team's approach to initiating possession from goal kicks and their effectiveness in establishing controlled possession from these situations. Calculated as the percentage of goal kicks that successfully lead to established possession beyond the initial receiving phase. Established possession is at least 8 sec, 4 passes and 4 different players. progcarry_df2[“time”] records the continued time of the game in seconds. progcarry_df2[“player_id”] identifies the player. Pass is progcarry_df2[“type_id”]==1 and goalkick is progcarry_df2[“type_id”]==124. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Buildup from goalkick %” 

# Variáveis 

# 18 

## # Progressive passes from middle third % 

"""Quantifies a team's ability to advance play forward through passing from the central zone of the pitch. It is the percentage of passes initiated in the middle third of the pitch that successfully progress the ball toward the opponent's goal. Calculated as: (Number of progressive passes from middle third ÷ Total passes attempted from middle third) × 100""" 

###CALCULATE 

### progcarry_df2 has progressive passes dummy 

## Context: 

You are a soccer analytics specialist. “Progressive passes from middle third %” quantifies a team's ability to advance play forward through passing from the central zone of the pitch. It is the percentage of passes initiated in the middle third of the pitch that successfully progress the ball toward the opponent's goal. Calculated as: (Number of progressive passes from middle third ÷ Total passes attempted from middle third) × 100. progcarry_df2 dataframe "progressive_pass" is a dummy that assigns 1 if the pass is progressive and 0 otherwise. “start_x” defines the initial x coordinate of a given event, while “end_x” defines its final coordinate. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Progressive passes from middle third %”. 

## # Variáveis 

## # 19 

## # Crosses per final third entry 

"""Quantifies a team's crossing tendency relative to their total attacking entries into the final third of the pitch. It is the frequency with which a team opts for crossing as an attacking strategy once they've entered the final third. Calculated as: (Total number of crosses attempted ÷ Total number of final third entries)""" 

## Context: 

You are a soccer analytics specialist. “Crosses per final third entry” quantifies a team's crossing tendency relative to their total attacking entries into the final third of the pitch. It is the frequency with which a team opts for crossing as an attacking strategy once they've entered the final third. It is calculated as: (Total number of crosses attempted ÷ Total number of final third entries). Open play Crosses, which is preferable, are defined as progcarry_df2[“type_id”]==1 and “qualifiers” == 2. “start_x” defines the initial x coordinate of a given event, while “end_x” defines its final coordinate. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “crosses per final third entry”. 

# Variáveis 

# 20 

# Dribbles per final third entry 

"""Quantifies a team's propensity to use individual dribbling skills as an attacking tool once they've advanced into the final third of the pitch. It is the frequency with which a team's players attempt to beat defenders through dribbling after entering the final third. Calculated as: (Total number of dribble attempts in final third ÷ Total number of final third entries)""" 

## Context: 

You are a soccer analytics specialist. “Dribbles per final third entry” quantifies a team's propensity to use individual dribbling skills as an attacking tool once they've advanced into the final third of the pitch. It is the frequency with which a team's players attempt to beat defenders through dribbling after entering the final third. Calculated as: (Total number of dribble attempts in final third ÷ Total number of final third entries). Successful dribbles are defined as progcarry_df2[“type_id”]==4 and “outcome” == 1. “start_x” defines the initial x coordinate of a given event, while “end_x” defines its final coordinate. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Dribbles per final third entry”. 

## # Variáveis 

# 21 

## # Box entries from crosses % 

"""It quantifies the proportion of a team's penalty area entries that come specifically from crossing situations rather than other attacking methods.It is the percentage of all successful entries into the opposition penalty box that originate from crosses. Calculated as: (Number of penalty box entries via crosses ÷ Total number of penalty box entries) × 100""" 

## Context: 

You are a soccer analytics specialist. “Box entries from crosses %” quantifies the proportion of a team's penalty area entries that come specifically from crossing situations rather than other attacking methods.It is the percentage of all successful entries into the opposition penalty box that originate from crosses. Calculated as: (Number of penalty box entries via crosses ÷ Total number of penalty box entries) × 100. 

Open play successful Crosses, which is preferable, are defined as progcarry_df2[“type_id”]==1 and  “outcome” == 1 and “qualifiers” == 2. “start_x” defines the initial x coordinate of a given event, while “end_x” defines its final coordinate. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Box entries from crosses %”. 

## # Variáveis 

## # 22 

## # Box entries from carries % 

"""Quantifies the proportion of a team's penalty area entries that come specifically from players dribbling or carrying the ball into the box rather than other attacking methods. It is the percentage of all successful entries into the opposition penalty box that occur via a player carrying the ball (dribbling) across the boundary. Calculated as: (Number of penalty box entries via carries/dribbles ÷ Total number of penalty box entries) × 100""" 

## Context: 

You are a soccer analytics specialist. “Box entries from carries %” quantifies the proportion of a team's penalty area entries that come specifically from players dribbling or carrying the ball into the box rather than other attacking methods. It is the percentage of all successful entries into the opposition penalty box that occur via a player carrying the ball (dribbling) across the boundary. Calculated as: (Number of penalty box entries via carries/dribbles ÷ Total number of penalty box entries) × 100. 

Successful dribbles are defined as progcarry_df2[“type_id”]==4 and “outcome” == 1. 

Carries are defined by progcarry_df2[“carry”]==1 

progcarry_df2[“start_x”] defines the initial x coordinate of a given event, while progcarry_df2[“end_x”] defines its final coordinate. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Box entries from carries %”. 

## # Variáveis 

## # Chance creation 

## # 23 

## # Shots from sustained attacks % 

"""Quantifies the proportion of a team's shots that originate from methodical, controlled possession sequences rather than from transitions, set pieces, or direct play. It is the percentage of total shots that result from extended possession-based attacking sequences. Calculated as: (Number of shots from sustained possession ÷ Total shots taken) × 100. 

Sustained attack: possession lasting min 9 seconds before the shot, involves min 4 consecutive completed passes prior to the shot.""" 

## Context: 

You are a soccer analytics specialist. “Shots from sustained attacks %” quantifies the proportion of a team's shots that originate from methodical, controlled possession sequences rather than from transitions, set pieces, or direct play. It is the percentage of total shots that result from extended possession-based attacking sequences. Calculated as: (Number of shots from sustained possession ÷ Total shots taken) × 100. progcarry_df2 dataframe identifies possession chains during football matches. “possessionId” numbers possession chains for each “team_id” (1, 2, 3…) independently. “first_chain”==1 marks the beginning of a chain, while “last_chain”==1 mark the ending of it. progcarry_df2[“time”] records the continued time of the game in seconds. progcarry_df2[“start_x”] defines the initial x coordinate of a given event, while progcarry_df2[“end_x”] defines its final coordinate. 

Shots are defined as “type_id”== [13, 14, 15, 16], excluding penalties which are “qualifiers”==9 as follows: 

np_shots = shots[~shots['qualifiers'].apply(lambda x: 9 in x and x[9] == True)] 

Sustained attack must satisfy the following conditions: possession lasting a minimum of 9 seconds before the shot, involves a minimum of 5 consecutive completed passes prior to the shot. 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Shots from sustained attacks %”. 

## # Variáveis 

## # 24 

# Shots from direct attacks % 

"""Quantifies the proportion of a team's shots that originate from rapid, vertical progression with minimal possession phases rather than methodical build-up play.It is the percentage of total shots that result from direct attacking sequences characterized by vertical progression and minimal passing. Calculated as: (Number of shots from direct attacks ÷ Total shots taken) × 100 

Direct attack: takes max 8 seconds from possession gain to shot, max 3 passes.""" Context: 

You are a soccer analytics specialist. “Shots from direct attacks %” quantifies the proportion of a team's shots that originate from rapid, vertical progression with minimal possession phases rather than methodical build-up play. It is the percentage of total shots that result from direct attacking sequences characterized by vertical progression and minimal passing. Calculated as: (Number of shots from direct attacks ÷ Total shots taken) × 100. 

progcarry_df2 dataframe identifies possession chains during football matches. “possessionId” numbers possession chains for each “team_id” (1, 2, 3…) independently. “first_chain”==1 marks the beginning of a chain, while “last_chain”==1 mark the ending of it. progcarry_df2[“time”] records the continued time of the game in seconds. progcarry_df2[“start_x”] defines the initial x coordinate of a given event, while progcarry_df2[“end_x”] defines its final coordinate. 

Shots are defined as “type_id”== [13, 14, 15, 16], excluding penalties which are “qualifiers”==9 as follows: 

np_shots = shots[~shots['qualifiers'].apply(lambda x: 9 in x and x[9] == True)] 

Direct attack: takes a maximum of 8 seconds from possession gain to shot, and a maximum of 4 passes. 

Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Shots from direct attacks %”. 

## # Variáveis 

## # 25 

# Shots per final third pass 

"""Quantifies a team's directness and shot generation rate relative to their passing volume in advanced areas. It is the ratio of shots generated compared to the number of passes a team completes in the final third. Calculated as: (Total shots taken ÷ Total passes completed in the final third)""" 

## Context: 

You are a soccer analytics specialist. “Shots per final third pass” quantifies a team's directness and shot generation rate relative to their passing volume in advanced areas. It is the ratio of shots generated compared to the number of passes a team completes in the final third. Calculated as: (Total shots taken ÷ Total passes completed in the final third). 

progcarry_df2[“start_x”] defines the initial x coordinate of a given event, while progcarry_df2[“end_x”] defines its final coordinate. Successful passes are progcarry_df2[“type_id”]==1, progcarry_df2[“outcome”]==1 

Shots are defined as “type_id”== [13, 14, 15, 16], excluding penalties which are “qualifiers”==9 as follows: 

np_shots = shots[~shots['qualifiers'].apply(lambda x: 9 in x and x[9] == True)] 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Shots per final third pass”. 

## # Variáveis 

## # 26 

## # Shots from outside the box % 

"""Quantifies the proportion of a team's total shots that are taken from beyond the penalty area boundary. It is the percentage of a team's total shots that originate from positions outside the 18-yard box. Calculated as: (Number of shots taken from outside the penalty area ÷ Total shots taken) × 100""" 

## Context: 

You are a soccer analytics specialist. “Shots from outside the box %” quantifies the proportion of a team's total shots that are taken from beyond the penalty area boundary. It is the percentage of a team's total shots that originate from positions outside the box. Calculated as: (Number of shots taken from outside the penalty area ÷ Total shots taken) × 100. 

progcarry_df2 dataframe identifies possession chains during football matches. progcarry_df2[“start_x”], progcarry_df2[“start_y”] define the initial coordinates of a given event, while progcarry_df2[“end_x”], progcarry_df2[“end_y”]  define its final coordinate. 

Shots are defined as “type_id”== [13, 14, 15, 16], excluding penalties which are “qualifiers”==9 as follows: 

np_shots = shots[~shots['qualifiers'].apply(lambda x: 9 in x and x[9] == True)] 

## Task: 

For each “game_id”, “team_id” write a code in Python to calculate “Shots from outside the box %”. 

