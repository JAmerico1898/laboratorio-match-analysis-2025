## **Estratégia de cálculo das métricas:** 

## **1. Bases de Dados necessárias e Métricas prévias:** 

- Events Data 

- Minutes played at the match level (per 90) 

- Action based xT from previous complete season 

- Location based xT 

## **2. Metrics computed at the Match Level (per 90)** 

## **2.1 Possession** 

- Home team possession 

- Away team possession 

## **2.2 Possession won per 90** 

_Number of recovered possessions adjusted by the opponent’s possession._ 

- Number of recovered possessions (dummy) 

## **2.3 Defensive actions per 90** 

_Number of successful defensive actions (such as defensive duels, tackles, interceptions, recoveries, and clearances) adj opp pos._ 

- Number of successful defensive duels, tackles, interceptions, recoveries, and clearances (dummy) 

## **2.4 Headed plays per 90** 

_Number of successful head passes or head shots in the attacking half adj pos._ 

- Number of successful head passes (dummy) 

- Number of successful head shots (dummy) 

## **2.5 Attacking aerials won per 90** 

_Percentage of attacking aerial duels won in the attacking 60% of the pitch (adj opp pos)._ 

- Attacking aerial duels won (by first contact) in the attacking 60% of the pitch (dummy) 

- Attacking aerial duels (by first contact) in the attacking 60% of the pitch (dummy) 

## **2.6 Aerials won per 90** 

_Number of aerial duels won (by first contact) per 90 minutes of play._ 

- Aerial duels won (by first contact) (dummy) 

## **2.7 Penalty area receptions per 90** 

_Number of successful best receptions inside the penalty area adj pos_ 

- Successful best receptions inside the penalty area (dummy) 

## **2.8 xG per 90** 

_Accumulated non penalty expected goals adj pos_ 

- Non-penalty shots (dummy) 

- Expected goals from the above 

## **2.9 Goals per 90** 

_Number of non-penalty goals adj pos_ 

**-** Non penalty goals (dummy) 

**2.10 Box entries per 90** 

_Number of ball carries into the penalty area (adj pos)_ 

**-** Ball carries into the penalty area (dummy) 

- penalty area 

## **2.11 Touches in box per 90** 

_Number of open play touches in opponent’s penalty area when in possession (passes, shots, carries, dribbles, touches)_ 

- Open play touches in opponent’s penalty area when in possession (passes, shots, carries, dribbles, touches) (dummy) 

## **2.12 Under pressure retention per 90** 

_Number of successful actions under pressure in the first or second thirds of the pitch (adj pos)_ 

- successful actions under pressure in the first or second thirds of the pitch (dummy) 

WHAT IS ACTIONS UNDER PRESSURE? 

## **2.13 Losses per 90** 

_Number of actions that end the possession of a team (passes, offensive duels, touches) (adj pos)._ 

- Actions that end the possession of a team (passes, offensive duels, touches) (dummy) 

## **2.14 High turnovers per 90** 

_Number of possessions lost (failed passes, bad ball touches or lost attacking duels) in own 40% of the pitch (adj pos)._ 

- Possessions lost (failed passes, bad ball touches or lost attacking duels) in own 40% of the pitch (dummy) 

## **2.15 Defensive aerials won per 90** 

_Number of defensive aerial duels won (by first contact) in the player's own 60% of the pitch (adj opp pos)._ 

- Defensive aerial duels won (by first contact) in the player's own 60% of the pitch (dummy) 

## **2.16 xG Dribble per 90** 

_Accumulated xG of shots within 5 seconds of dribbles in the same possession assigned to the dribbler adjusted by possession._ 

- Dribbles that led to shots within 5 seconds in the same possession assigned to the dribbler (dummy) 

- xG from the shots above 

## **2.17 Dribbles xT per 90** 

_Accumulated location based xT from successful dribbles (adj pos)._ 

- successful dribbles (dummy) 

- xT of the above 

## **2.18 Possessions won per opponent possession** 

_Number of recovered possessions adj opp pos divided by total number of opponent possessions._ 

- Recovered possessions (dummy) 

- Opponent’s possessions (dummy). 

NÃO MENCIONA PER 90, MAS TRATEI ASSIM 

## **2.19 xGOT per 90** 

_Accumulated non penalty expected goals on target (adj pos)._ 

- Shots on target (dummy) 

- xG of the above 

## **2.20 Goals per 90** 

_Number of non-penalty goals (adj pos)._ 

- non-penalty goals (dummy) 

## **2.21 Long ball receptions per 90** 

_Number of successful long ball receptions divided by the team's possession percentage multiplied by 0.5._ 

- Successful long ball receptions (dummy) 

- Long balls in the previous pass (dummy) 

## **2.22 Linkups per 90** 

- Number of successful linkup-plays (an action of an attacking player receiving a ball from a defender or a midfielder with his back to the opposite goal) (adj pos). 

COMO IDENTIFICAR LINKUP PLAY? 

## **2.23 Interceptions per 90** 

_Number of interceptions (adj opp pos)._ 

- Interceptions (dummy) 

## **2.24 Counterpressing per 90** 

_Number of recoveries in duels that end a possession of the opposition team within less than 5 seconds, adjusted by the opponent's possession_ 

- Recoveries in duels that end a possession of the opposition team within less than 5 seconds (dummy) 

## **2.25 Ball recoveries per 90** 

_Number of ball recoveries that do not happen with an active defensive action (such as tackles, duels, or interceptions) adj opp pos._ 

- Ball recoveries that do not happen with an active defensive action (such as tackles, duels, or interceptions) (dummy) 

## **2.26 xG Buildup per 90** 

_Accumulated non-penalty XG for possessions in which the player is involved in at least one event, excluding shots and shot assists (adj pos)._ 

- possession that led to a shot (dummy) 

## **2.27 Touches per 90** 

_Number of open play touches when in possession (passes, shots, carries, dribbles, touches) adj pos._ 

- open play touches when in possession (passes, shots, carries, dribbles, touches) (dummy) 

## **2.28 Aerials per 90** 

_Number of aerial duels a player engages._ 

- Aerial duels (dummy). 

## **2.29 Creative passes per 90** 

_Number of assists, key passes, shot assists, and second assists (adj pos)_ 

- Creative passes (assists, key passes, shot assists, and second assists ) (dummy) 

## **2.30 Passes third (xT) per 90** 

_Accumulated action-based xT from successful open play passes inside of the final third._ 

- Successful open play passes inside of the final third (dummy) 

- xT of the above 

## **2.31 Passes into Third (xT) per 90** 

_Accumulated action-based xT from successful open play passes into the final third._ 

- Successful open play passes into the final third (dummy) 

- xT of the above 

## **2.32 Passes (xT) per 90** 

_Accumulated action-based xT from open play passes (adj pos)._ 

- Open play passes (dummy) 

- xT of the above 

## **2.33 Crosses (xT) per 90** 

_Accumulated action-based expected threat (xT) of successful crosses (adj pos)_ 

- Successful crosses (dummy) 

- xT of the above 

## **2.34 xG per 90** 

_Accumulated non-penalty expected goals (adj pos)._ 

- Non-penalty shots. 

- xG of the above 

## **2.35 High recoveries per 90** 

_Number of recovered possessions in the attacking half (adj opp pos)._ 

- Recovered possessions in the attacking half (dummy) 

## **2.36 Defensive intensity per 90** 

_Number of defensive duels, loose ball duels, interceptions, tackles and fouls when out of possession (adj opp pos)._ 

- Defensive duels (loose ball duels, interceptions, tackles and fouls) out of possession (dummy) 

## **2.37 Playmaking passes per 90** 

_Number of successful open play progressive passes, smart passes, through passes, and passes into the final third (adj pos)._ 

- open play progressive passes, smart passes, through passes, and passes into the final third (dummy) 

**2.38 Passes into third (xT) per 90** 

_Accumulated action-based xT from successful open play passes into the final third._ 

- Open play passes into the final third (dummy) 

- xT of open play passes into the final third 

## **2.39 Ball progression (xT) per 90** 

_Action-based expected threat (xT) from successful progressive passes and progressive carries that end in the opponent's half (adj pos)._ 

- successful progressive passes that end in the opponent's half 

- successful progressive carries that end in the opponent's half 

- xT of the above 

## **2.40 xGCreated per 90** 

_Accumulated XG of shots within 5 seconds of passes in the same possession assigned to the passer (adj pos)._ 

- passes that led to shots within 5 seconds in the same possession 

- xG of these shots 

## **2.41 Second assists per 90** 

_Number of last actions of a player assist by a teammate adj pos._ 

- Passes that led to assists (dummy) 

## **2.42 Key passes per 90** 

_Number of passes that immediately create a clear goal scoring opportunity for a teammate (adj pos)._ 

- Key pass (dummy) 

## **2.43 Deep completions per 90** 

_Number of successful non-cross passes into the area within 20 meters of the opponent's goal (adj pos)_ 

- Successful non-cross passes into the area within 20 meters of the opponent's goal 

- Distance from pass to the goal 

## **2.44 xA per 90** 

_Accumulated xA (adj pos)._ 

- xA 

HOW TO COMPUTE xA? 

## **2.45 Assists per 90** 

_Number of assists a player provides._ 

- Passes that led to shots (dummy) 

## **2.46 Carries (xT) per 90** 

Accumulated expected threat (xT) from ball carries (adj pos). 

- Carries (dummy) 

- xT of the above 

## **2.47 Deep runs (xT) per 90** 

_Accumulated action-based expected threat (xT) from through ball receptions (adj pos)_ 

- Through ball receptions (dummy) 

- xT of the above 

## **2.48 Ball runs (xT) per 90** 

_Accumulated location-based expected threat (xT) from progressive runs and high-speed runs with the ball (adj pos)._ 

- Progressive runs with the ball (dummy) 

- High speed runs with the ball (dummy) 

- Speed of the run 

- Location-based expected threat (xT) of the above 

HOW TO DEFINE RUNS AND HIGH-SPEED RUNS? 

## **2.49 True tackles won per 90** 

_Number of defending 1v1s and sliding tackles that stopped progression of a player or recovered the possession (adj opp pos)._ 

- Defending 1v1 (dummy) 

- sliding tackles that stopped progression of a player (x final < x initial) (dummy) 

- sliding tackles that recovered possession (dummy) 

HOW TO COMPUTE 1V1? 

## **2.50 Defensive duels won per 90** 

_Number of defensive ground duels that stopped progression of a player or recovered the possession (adj opp pos)._ 

- defensive ground duels (such as defensive duels, tackles, interceptions, recoveries, and clearances) that stopped progression of a player or recovered the possession (dummy) 

## **Aerials won per 90** 

Number of aerial duels won (by first contact) per 90 minutes of play. 

- Aerial duels won (dummy) 

## **3. Metrics computed at the Match %** 

## **3.1 Tackle success %** 

_Percentage of defending 1v1s and sliding tackles won_ 

- defending 1v1s 

- sliding tackles won 

## **3.2 Defending 1v1 %** 

_Percentage of successful attempts by a player to prevent an opposing player in possession of the ball from dribbling past them_ 

- Dribbles attempted against 

- Dribbles avoided 

HOW TO COMPUTE DRIBBLES ATTEMPTED AND DRIBBLES AVOIDED 

## **3.3 Attacking aerials won %** 

_Percentage of attacking aerial duels won in the attacking 60% of the pitch_ 

- attacking aerial duels won in the attacking 60% of the pitch 

- total number of attacking aerial duels in the attacking 60% of the pitch 

## **3.4 Aerials won %** 

_Percentage of aerial duels won_ 

- number of aerial duels won (by first contact) 

- total number of aerial duels contested 

## **3.5 Opposition progressive passes from defensive area %** 

_Percentage of the opponent’s passes originating from within the player’s defensive area that are successful, progressive and have an end location in the attacking half_ 

- number of opponent’s passes originating from within the player’s defensive area that are successful, progressive and have an end location in the attacking half 

- total opponent’s passes originating from within the player’s defensive area and have an end location in the attacking half 

## **3.6 Opposition xT from defensive area** 

_Accumulated action-based xT per 100 successful opponent passes originating from within the players defensive area._ 

- Accumulated opponent action-based xT 

- successful opponent passes originating from within the players defensive area 

## **3.7 Opposition xG from defensive area** 

_Accumulated non penalty xG from the opponent’s shots that were a part of possessions that had a successful pass originating from within the player’s defensive area, measured per 100 opponent possessions._ 

- Accumulated non penalty xG from the opponent’s shots that were a part of possessions that had a successful pass originating from within the player’s defensive area. 

- number of opponent possessions. 

## **3.8 Opposition xG after defensive action** 

_Accumulated non penalty xG from the opponent’s shots that were a part of possessions that had a successful pass originating from within the player’s defensive area, measured per 100 opponent possessions._ 

- Accumulated not penalty XG from the opponent’s shots where the player had the last defensive action before the shot 

- shot occurred within 8 seconds of the action 

- number of possessions 

WHAT IS THE PLAYER’S DEFENSIVE AREA? 

ALL METRICS IN CHANCE PREVENTION WORK THE OTHER WAY AROUND. REORDER INVERSELY 

## **3.9 Pressure resistance %** 

Number of successful actions under pressure in the first or second thirds of the pitch 

WHAT ARE ACTIONS UNDER PRESSURE? 

## **3.10 Defensive aerials won %** 

_Percentage of defensive aerial duels won in the player's own 60% of the pitch._ 

- defensive aerial duels won in the player's own 60% of the pitch. 

- total aerial duels won in the player's own 60% of the pitch. 

## **3.11 Dribbles success %** 

_The ratio between successful dribbles and total dribbles._ 

- successful dribbles 

- total dribbles. 

## **3.12 xG per shot** 

Accumulated non-penalty xG compared to the number of shots. 

- Accumulated non-penalty xG 

- Total number of shots. 

## **3.13 xG + xA per 100 touches** 

_The sum of accumulated non penalty xG and xA divided by the number of touches and multiplied it by 100._ 

- Accumulated non penalty xG 

- Accumulated non penalty xA 

- Number of touches 

## **3.14 High turnovers per low reception** 

_Number of possessions lost (failed passes, bad ball touches or loss attacking duels) compared to total number of ball receptions in own 40% of the pitch._ 

- Number of possessions lost (failed passes, bad ball touches or loss attacking duels) 

- Total number of ball receptions in own 40% of the pitch. 

## **3.15 xG chain per possession** 

_Accumulated non-penalty xG for possessions in which a player is involved in at least one event divided by total number of possession involvements._ 

- Accumulated non-penalty xG for possessions in which a player is involved in at least one event 

- Total number of possession involvements. 

## **3.16 Carries (xT) per 100 receptions** 

Accumulated expected threat (xT) from carries divided by the number of receptions and multiplied by 100. 

- Accumulated expected threat (xT) from carries 

- Number of receptions 

## **3.17 Passes (xT) per 100 receptions** 

_Accumulated xT from passes compared to the number of shots and multiplied by 100._ 

- Accumulated xT from passes 

- Total number of shots 

## **3.18 Goals – xG** 

_The difference between non penalty goals scored and non-penalty expected goals._ 

- Non penalty goals scored 

- Non penalty expected goals. 

## **3.19 Shot conversion %** 

_Percentage off no penalty shots that are goals._ 

Non-penalty shots 

Non-penalty goals. 

## **3.20 xG per box touch** 

_Accumulated no penalty XG compared to the number of penalty area touches._ 

- Accumulated non-penalty xG 

- Number of penalty area touches. 

## **3.21 Goals per box touch** 

_Number of non-penalty goals compared to the number of penalty area touches._ 

- Number of non-penalty goals 

- Number of penalty area touches. 

## **3.22 xG per shot** 

_Accumulated no penalty XG compared to the number of shots theory._ 

- Accumulated non-penalty XG 

- Number of shots 

## **3.23 Opposition pass success % into defensive area** 

_Percentage of the opponents passes into the players defensive area that are successful._ 

- Opponents’ passes into the players defensive area that are successful 

- Total opponents’ passes into the players defensive area 

- **3.24 Opposition xT into defensive area** 

_Accumulated action-based XT per 100 successful opponent passes into the players defensive area._ 

- Accumulated action-based XT into the players defensive area. 

- Successful opponent passes into the players defensive area. 

## **3.25 Defensive area (m[2] )** 

_The size of the area, measured in squared metres, that a player covers defensively in open play. It is measured as the area that covers 68% of the players open played defensive actions (adj opp pos)._ 

## **3.26 Defensive line height (m)** 

_Average heights on the pitch, measured in metres, of the players defensive actions._ 

## **3.27 Succesful 1v1 per 90** 

_Number of successful attempts to prevent an opposing player in possession of the ball to dribble past the player (adj opp pos)._ 

- Dribbles succeeded 

- Dribbles attempts 

HOW TO COMPUTE DRIBBLES ATTEMPTED AND DRIBBLES CONCEDED 

## **3.28 Defensive duels won %** 

_Number of defensive ground duels that stopped progression of a player or recovered the possession (adj opp pos)._ 

- Successful defensive ground duels 

- Total defensive ground duels 

