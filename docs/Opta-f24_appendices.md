**==> picture [596 x 191] intentionally omitted <==**

**==> picture [106 x 49] intentionally omitted <==**

**F24: Feed appendices document Supplementary information to F24** 

**==> picture [596 x 68] intentionally omitted <==**

## **Contents** 

|Appendix|1 – event types|1|
|---|---|---|
|Appendix|2 – qualifier types|4|
|Appendix|3 – useful queries|16|
|Appendix|4 – assist and keypass interpretation|19|
|Appendix|5 – the <Event> tag|20|
|Appendix|6 – how events are deleted|21|
|Appendix|7 – how events are edited/modified|22|
|Appendix|8 – outcome definitions|23|
|Appendix|9 – associated qualifiers|25|
|Appendix|10 – period ID list|27|
|Appendix|11 – pitch co-ordinates and direction of play|27|
|Appendix|12 – goalmouth co-ordinates|28|
|Appendix|13 – pitch zones|29|
|Appendix|14 - playing positions|30|



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

1 

## **Appendix 1 – event types** 

## Event types 

The following table details the events types used in the F24 feed: 

|**Event id**|**Name**|**Description**|
|---|---|---|
|1|Pass|Any pass attempted from oneplayer to another – free kicks,corners,throw ins, goal kicks andgoal assists|
|2|Offside Pass|Attemptedpass made to aplayer who is in an offsideposition|
|3|Take On|Attempted dribble past an opponent (excluding when qualifier 211 is present as this is ‘overrun’ and is not always<br>a duel event)|
|4|Foul|This event is shown when a foul is committed resultingin a free kick|
|5|Out|Shown each time the ballgoes out ofplayfor a throw-in orgoal kick|
|6|Corner Awarded|Ballgoes out ofplayfor a corner kick|
|7|Tackle|Tackle = dispossesses an opponent of the ball - Outcome 1 = win & retain possession or out of play, 0 = win<br>tackle but notpossession|
|8|Interception|When a player intercepts any pass event between opposition players and prevents the ball reaching its target.<br>Cannot be a clearance.|
|9|Turnover|Unforced error / loss of possession - i.e. bad control of ball – NO LONGER USED (Replaced with Unsuccessful<br>Touch + Overrun)|
|10|Save|Goalkeeper event;savinga shot ongoal. Can also be an outfieldplayer event withqualifier 94 for blocked shot|
|11|Claim|Goalkeeper event;catchinga crossed ball|
|12|Clearance|Player underpressure hits the ball clear of the defensive zone or/and out ofplay|
|13|Miss|Anyshot ongoal whichgoes wide or over thegoal|
|14|Post|Whenever the ball hits the frame of thegoal|
|15|Attempt Saved|Shot saved - this event is for theplayer who made the shot. Qualifier 82 can be added for blocked shot.|
|16|Goal|Allgoals|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

2 

|**Event id**|**Name**|**Description**|
|---|---|---|
|17|Card|Bookings;will have red, yellow or 2ndyellowqualifierplus a reason|
|18|Player off|Player is substituted off|
|19|Player on|Player comes on as a substitute|
|20|Player retired|Player is forced to leave thepitch due to injuryand the team have no substitutions left|
|21|Player returns|Player comes back on thepitch|
|22|Player becomesgoalkeeper|When an outfieldplayer has to replace thegoalkeeper|
|23|Goalkeeper becomesplayer|Ifgoalkeeper becomes an outfieldplayer|
|24|Condition change|Change inplayingconditions|
|25|Official change|Referee or linesman is replaced|
|27|Start delay|Used when there is a stoppage inplaysuch as aplayer injury|
|28|End delay|Used when the stoppage ends andplayresumes|
|30|End|End of a matchperiod|
|32|Start|Start of a matchperiod|
|34|Team set up|Team line up; qualifiers 30,44,59,130,131 will showplayer line upand formation|
|35|Player changedposition|Player moved to a differentposition but the team formation remained the same|
|36|Player changed Jersey<br>number|Player is forced to change jersey number, qualifier will show the new number|
|37|Collection End|Event 30 signals end of half. This signals end of the match and thus data collection.|
|38|Temp_Goal|Goal has occurred but it ispendingadditional detailqualifiers from Opta. Will change to event 16.|
|39|Temp_Attempt|Shot ongoal has occurred but ispendingadditional detailqualifiers from Opta. Will change to event 15.|
|40|Formation change|Team alters its formation|
|41|Punch|Goalkeeper event;ball ispunched clear|
|42|Good Skill|Aplayer shows agoodpiece of skill on the ball – such as a stepover or turn on the ball – NO LONGER USED|
|43|Deleted event|Event has been deleted – the event will remain as it was originally with the same ID but will be resent with the<br>type altered to 43.|
|44|Aerial|Aerial duel – 50/50 when the ball is in the air – outcome will represent whether the duel was won or lost|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

3 

|**Event id**|**Name**|**Description**|
|---|---|---|
|45|Challenge|When aplayer fails to win the ball as an opponent successfullydribblespast them|
|47|Rescinded card|This can occurpost match if the referee rescinds a card he has awarded|
|49|Ball recovery|Team wins the possession of the ball and successfully keeps possession for at least two passes or an attacking<br>play|
|50|Dispossessed|Player is successfullytackled and losespossession of the ball|
|51|Error|Mistake by player losingthe ball. Leads to a shot orgoals as described withqualifier 169 or 170|
|52|Keeperpick-up|Goalkeeper event; picks upthe ball|
|53|Cross not claimed|Goalkeeper event;cross not successfullycaught|
|54|Smother|Goalkeeper event;comes out and covers the ball in the box winning possession|
|55|Offsideprovoked|Awarded to last defender when an offside decision isgiven against an attacker|
|56|Shield ball opp|Defender uses his bodyto shield the ball from an opponent as it rolls out ofplay|
|57|Foul throw-in|A throw-in not taken correctlyresultingin the throw beingawarded to the opposingteam|
|58|Penaltyfaced|Goalkeeper event; penaltybyopposition team|
|59|Keeper Sweeper|When keeper comes off his line and/or out of his box to clear the ball|
|60|Chance missed|Used when a player does not actually make a shot on goal but was in a good position to score and only just<br>missed receivingapass|
|61|Ball touch|Used when a player makes a bad touch on the ball and loses possession. Outcome 1 – ball simply hit the player<br>unintentionally. Outcome 0 – Player unsuccessfullycontrolled the ball.|
|63|Temp_Save|An event indicating a save has occurred but without full details. Event 10 will follow shortly afterwards with full<br>details.|
|64|Resume|Match resumes on a new date after beingabandoned midgame.|
|65|Contentious referee<br>decision|Any major talking point or error made by the referee – decision will be assigned to the relevant team|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

4 

## **Appendix 2 – qualifier types** 

## Qualifier types 

These tables highlight the list of `qualifier_id` attributes that we include in this feed. 

An appendix follows that details the list of `qualifier_id` attributes that you can reasonably expect to see against an associated `type_id` . 

The following tables detail the qualifiers that you should expect to see in F24: 

|**ID**|**Pass Events**|**Values**|**Description - ASSOCIATED TO EVENT TYPE 1**|
|---|---|---|---|
|**1**|Longball||Long pass over 35yards|
|**2**|Cross||A ballplayed in from wide areas into the box|
|**3**|Headpass||Pass made with aplayers head|
|**4**|Through ball||Ballplayed through forplayer makingan attackingrun to create a chance ongoal|
|**5**|Free kick taken||Anyfree kick;direct or indirect|
|**6**|Corner taken||All corners. Look forqualifier 6 but excluding qualifier 2 for short corners|
|**7**|Players caught offside|Player ID|Player who was in an offsideposition whenpass was made.|
|**8**|Goal disallowed||Pass led to agoal disallowed for a foul or offside|
|**106**|AttackingPass||Apass in the opposition’s half of thepitch|
|**107**|Throw-in||Throw-in taken|
|**140**|Pass End X|0-100|The xpitch coordinate for the endpoint of apass - See Appendix 5|
|**141**|Pass End Y|0-100|They pitch coordinate for the endpoint of apass - See Appendix 5|
|**155**|Chipped||Pass which was chipped into the air|
|**156**|Lay-off||Pass whereplayer laid the ball into thepath of a teammates run|
|**157**|Launch||Pass played from a player’s own half up towards front players. Aimed to hit a zone rather<br>than a specificplayer|
|**168**|Flick-on||Pass where aplayer has "flicked" the ball forward usingtheir head|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

5 

|**ID**|**Pass Events**|**Values**|**Description - ASSOCIATED TO EVENT TYPE 1**|
|---|---|---|---|
|**195**|Pull Back||Player in opposition’s penalty box reaches the by-line and passes (cuts) the ball backwards<br>to a teammate|
|**196**|Switch of play||Any pass which crosses the centre zone of the pitch and in length is greater than 60 on the y<br>axis of thepitch|
|**210**|Assist||The pass was an assist for a shot. The type of shot then dictates whether it was a goal assist<br>orjust key pass.|
|**212**|Length|Dynamic - yards of<br>pitch|The estimated length the ball has travelled during the associated event.|
|**213**|Angle|0 to 6.28 (Radians)|The angle the ball travels at during an event relative to the direction of play. Shown in<br>radians.|
|**218**|2nd assist||Pass was deemed a 2nd assist - created the opportunityfor anotherplayer to assist agoal|
|**219**|Players on both posts||Assigned to event 6 indicating there were defensive players on both posts when a corner<br>was taken|
|**220**|Player on near post||Assigned to event 6 indicating there was a defensive player on only the near post when a<br>corner was taken|
|**221**|Player on far post||Assigned to event 6 indicating there was a defensive player on only the far post when corner<br>was taken|
|**222**|No players on posts||Assigned to event 6 indicating there were no defensive players on either post when a corner<br>was taken|
|**223**|In-swinger||Corner was crossed into the box swervingtowards thegoal|
|**224**|Out-swinger||Corner was crossed into the  box swervingawayfrom thegoal|
|**225**|Straight||Corner was crossed into the box with a straight ball flight|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

6 

|**ID**|**Body Part**|**Values**|**Description**|
|---|---|---|---|
|**15**|Head||Anyevent where theplayer used their head such as a shot or a clearance|
|**72**|Left footed||Player shot with their left foot|
|**20**|Right footed||Player shot with right footed|
|**21**|Other body part||Shot was neither via aplayer’s head or foot for example knee or chest|
|||||
|**ID**|**Pattern of Play**|**Values**|**Description - ASSOCIATED TO EVENT TYPES 13, 14, 15, 16**|
|**22**|Regularplay||Shot duringopenplayas opposed to from a setplay|
|**23**|Fast break||Shot occurred followinga fast break situation|
|**24**|Setpiece||Shot occurred from a crossed free kick|
|**25**|From corner||Shot occurred from a corner|
|**26**|Free kick||Shot occurred directlyfrom a free kick|
|**96**|Corner situation||Pass or shot event in corner situation. 25 is used when the goal is direct from corner, 96<br>relates to 2ndphase attack.|
|**97**|Direct free||26 will be used for shot directly from a free kick. 97 only used with Opta GoalData (game<br>system 4)but not with full data.|
|**112**|Scramble||Goal where there was a scramble for possession of the ball and the defence had an<br>opportunityto clear|
|**160**|Throw-in setpiece||Shot came from a throw-in setpiece|
|**29**|Assisted||Indicates that there was apass(assist)from anotherplayer to set upthegoal opportunity|
|**154**|Intentional assist||Shot from an intentional assist i.e. The assisting player intended thepass,no deflection etc|
|**55**|Related event ID|Event_id|This will appear for goals or shots, the related event_id will be that of the assist and thus<br>show the assisting player ID|
|**216**|2nd related event ID|Event_id|If there was a 2nd assist, i.e a pass to create the opportunity for the player making the assist.<br>MLS and German Bundesliga 1 & 2.|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

7 

|**ID**|**Shot Descriptors**|**Values**|**Description - ASSOCIATED TO EVENT TYPES 13, 14, 15, 16**|
|---|---|---|---|
|**9**|Penalty||When attempt on goal was a penalty kick. ALSO used on Event type 4 to indicate a penalty<br>was awarded|
|**28**|Owngoal||Owngoal ._Note: Use the inverse coordinates of thegoal location_|
|||||
|||||
|||||
|||||
|**113**|Strong||Shot was subjectivelyclassed as strong|
|**114**|Weak||Shot was subjectivelyclassed as weak|
|**115**|Rising||Shot was risingin the air|
|**116**|Dipping||Shot was dippingtowards theground|
|**117**|Lob||Shot was an attempt bythe attacker toplaythe ball over thegoalkeeper and into thegoal|
|||||
|||||
|**120**|Swerve Left||Shot which swerves to the left - from attackersperspective|
|**121**|Swerve Right||Shot which swerves to the right - from attackersperspective|
|**122**|Swerve Moving||Shot which swerves in several directions|
|**133**|Deflection||Shot deflected off anotherplayer|
|**136**|Keeper Touched||Goal where thegoalkeepergot a touch on the ball as it went in|
|**137**|Keeper Saved||Shot going wide or over the goal but still collected/saved by the goalkeeper with event type<br>15|
|**138**|Hit Woodwork||Anyshot which hits thepost or crossbar|
|**153**|Notpastgoal line||Shot missed which does notpass thegoal line|
|**214**|Big Chance||Shot was deemed by Opta analysts an excellent opportunity to score – clear cut chance eg<br>one on one|
|**215**|Individual Play||Player created the chance to shoot by himself, not assisted. For example he dribbled to<br>create space for himself and shot.|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

8 

|**ID**|**Shot Descriptors**|**Values**|**Description - ASSOCIATED TO EVENT TYPES 13, 14, 15, 16**|
|---|---|---|---|
|**217**|2nd assisted||Indicates that this shot had a significant pass to create the opportunity for the pass which led<br>to agoal|
|**228**|Own shot blocked||Player blocks an attackingshot  unintentionallyfrom their teammate|



|**ID**|**Shot Location Descriptors**|**Values**|**Description**|
|---|---|---|---|
|**16**|Small box-centre||Zone of thepitch - See appendix 7|
|**17**|Box-centre||Zone of thepitch - See appendix 7|
|**18**|Out of box-centre||Zone of thepitch - See appendix 7|
|**19**|35+ centre||Zone of thepitch - See appendix 7|
|**60**|Small box-right||Zone of thepitch - See appendix 7|
|**61**|Small box-left||Zone of thepitch - See appendix 7|
|**62**|Box-deepright||Zone of thepitch - See appendix 7|
|**63**|Box-right||Zone of thepitch - See appendix 7|
|**64**|Box-left||Zone of thepitch - See appendix 7|
|**65**|Box-deepleft||Zone of thepitch - See appendix 7|
|**66**|Out of box-deepright||Zone of thepitch - See appendix 7|
|**67**|Out of box-right||Zone of thepitch - See appendix 7|
|**68**|Out of box-left||Zone of thepitch - See appendix 7|
|**69**|Out of box-deepleft||Zone of thepitch - See appendix 7|
|**70**|35+ right||Zone of thepitch - See appendix 7|
|**71**|35+ left||Zone of thepitch - See appendix 7|
|**73**|Left||Hit the leftpost or missed left|
|**74**|High||Hit crossbar or missed over|
|**75**|Right||Hit rightpost or missed right|
|**76**|Low left||Zone of thegoalmouth - See appendix 6|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

9 

|**ID**|**Shot Location Descriptors**|**Values**|**Description**|
|---|---|---|---|
|**77**|High left||Zone of thegoalmouth - See appendix 6|
|**78**|Low centre||Zone of thegoalmouth - See appendix 6|
|**79**|High centre||Zone of thegoalmouth - See appendix 6|
|**80**|Low right||Zone of thegoalmouth - See appendix 6|
|**81**|High right||Zone of thegoalmouth - See appendix 6|
|**82**|Blocked||Zone of thegoalmouth - See appendix 6|
|**83**|Close left||Zone of thegoalmouth - See appendix 6|
|**84**|Close right||Zone of thegoalmouth - See appendix 6|
|**85**|Close high||Zone of thegoalmouth - See appendix 6|
|**86**|Close left and high||Zone of thegoalmouth - See appendix 6|
|**87**|Close right and high||Zone of thegoalmouth - See appendix 6|
|**100**|Sixyard blocked||Shot blocked on the 6yard line|
|**101**|Saved off line||Shot saved on thegoal line|
|**102**|Goal mouthyco-ordinate|0-100|Y Co-ordinate of where a shot crossed goal line - see Appendix 4<br>Z Co-ordinate for height at which a shot crossed thegoal line - see Appendix 4|
|**103**|Goal mouth z co-ordinate|0-100||
|||||
|||||
|**146**|Blocked x co-ordinate|0-100|The xpitch coordinate for where a shot was blocked|
|**147**|Blockedyco-ordinate|0-100|They pitch coordinate for where a shot was blocked|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

10 

|**ID**|**Foul & Card Events**|**Values**|**Description - ASSOCIATED TO EVENT TYPE 4 except for cards**|
|---|---|---|---|
|**10**|Hand||Handball|
|**11**|6-seconds violation||Goalkeeper held onto the ball longer than 6 seconds resultingin a free kick|
|**12**|Dangerousplay||A foul due to dangerousplay|
|**13**|Foul||All fouls|
|**31**|Yellow Card||Player shown ayellow card|
|**32**|Secondyellow||Player receives a 2ndyellow card which automaticallyresults in a red card|
|**33**|Red card||Player shown a straight red card|
|**34**|Referee abuse||Card shown toplayer because of abuse to the referee|
|**35**|Argument||Card shown toplayer because of an argument|
|**36**|Fight||Card shown toplayer because of their involvement in a fight|
|**37**|Time wasting||Card shown toplayer for time wasting|
|**38**|Excessive celebration||Card shown toplayer for excessivelycelebratingagoal|
|**39**|Crowd interaction||Card shown toplayer because of contact or communication with the crowd|
|**40**|Other reason||Card shown for unknown reason|
|**95**|Back pass||Free kick given for an illegal pass to the goalkeeper which was collected by his hands or picked<br>up|
|**132**|Dive||Free kick or card event; playerpenalised for simulation|
|**158**|Persistent infringement||Card shown toplayer forpersistent fouls|
|**159**|Foul and abusive language||Card shown forplayer usingfoul language|
|**161**|Encroachment||Card shown forplayer who moves within 10yards of an opponent’s free kick|
|**162**|Leavingfield||Card shown forplayer leavingthe field withoutpermission|
|**163**|Enteringfield||Card shown forplayer enteringthe field during playwithout referee'spermission|
|**164**|Spitting||Card shown for spitting|
|**165**|Professional foul||Card shown for a deliberate tactical foul|
|**166**|Handlingon the line||Card shown to an outfieldplayer for usingtheir hand to keepthe ball out of thegoal|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

11 

|**ID**|**Foul & Card Events**|**Values**|**Description - ASSOCIATED TO EVENT TYPE 4 except for cards**|
|---|---|---|---|
|**171**|Rescinded card||Referee rescind a cardpost match|
|**172**|No impact on timing||Player booked on bench but who hasn'tplayed anyminutes in the match|
|**184**|Dissent||Cad shown when aplayer does not obeyreferee instructions|
|**191**|Off the ball foul||Foul committed byand on aplayer who is not inpossession of the ball|
|**192**|Block byhand||Outfieldplayer blocks a shot with their hand|



|**ID**|**Goalkeeper Events**|**Values**|**Description - EVENT TYPES 10, 11, 12**|
|---|---|---|---|
|**190**|From shot off target||Used with Event 10. Indicates a shot was saved by the goalkeeper but in fact the shot was<br>goingwide and not on target|
|**88**|High claim||Event 11 Claim - Goalkeeper claimspossession of a crossed ball|
|**89**|1 on 1||Event 10 Save;when attacker was clear with no defenders between him and thegoalkeeper|
|**90**|Deflected save||Event 10 Save;whengoalkeeper saves a shot but does not catch the ball|
|**91**|Dive and deflect||Event 10 Save;whengoalkeeper saves a shot while divingbut does not catch the ball|
|**92**|Catch||Event 10 Save;whengoalkeeper saves a shot and catches it|
|**93**|Dive and catch||Event 10 Save;whengoalkeeper saves a shot while divingand catches it|
|**123**|Keeper Throw||Pass event -goalkeeper throws the ball out|
|**124**|Goal Kick||Pass event –goal kick|
|**128**|Punch||Clearance by goalkeeper where hepunches the ball clear|
|**139**|Own Player||Shot saved by goalkeeper that was deflected bya defender|
|**173**|Parried safe||Goalkeeper save where shot isparried to safety|
|**174**|Parried danger||Goalkeeper save where shot isparried but onlyto another opponent|
|**175**|Fingertip||Goalkeeper save usinghis fingertips|
|**176**|Caught||Goalkeeper catches the ball|
|**177**|Collected||Goalkeeper save and collectspossession of the ball|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

12 

|**ID**|**Goalkeeper Events**|**Values**|**Description - EVENT TYPES 10, 11, 12**|
|---|---|---|---|
|**178**|Standing||Goalkeeper save while standing|
|**179**|Diving||Goalkeeper save while diving|
|**180**|Stooping||Goalkeeper saves while stooping|
|**181**|Reaching||Goalkeeper save wheregoalkeeper reaches for the ball|
|**182**|Hands||Goalkeeper saves with his hands|
|**183**|Feet||Goalkeeper save usinghis feet|
|**186**|Scored||Goalkeeper event - shots faced and not saved resultingingoal|
|**187**|Saved||Goalkeeper event - shots faced and saved|
|**188**|Missed||Goalkeeper event - shot faced which went wide or over. Did not require a save.|
|**198**|GK hoof||Goalkeeper drops the ball on the ground and kicks it long towards a position rather than a<br>specificplayer|
|**199**|Gk kick from hands||Goalkeeper kicks the ball forward straight out of his hands|



|**ID**|**Defensive Events**|**Values**|**Description**|
|---|---|---|---|
|**14**|Last line||When a player makes a defensive action and they are the last person between the opponent<br>and thegoal|
|**94**|Def block||Defender blocks an opposition shot. Shown with event 10.|
|**167**|Out ofplay||Tackle or clearance event sent the ball out ofplay|
|**169**|Leadingto attempt||Aplayer error,event 51,which leads to an opponent shot ongoal|
|**170**|Leadingtogoal||Aplayer error,event 51,which lead to an opponent scoringagoal|
|**185**|Blocked cross||Clearance;cross is blocked|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

13 

|**ID**<br>**Line Up / Subs /**<br>**Formation**|**ID**<br>**Line Up / Subs /**<br>**Formation**|**Values**<br>**Description - ASSOCIATED WITH EVENT TYPES 32, 34, 35, 36, 40**|**Values**<br>**Description - ASSOCIATED WITH EVENT TYPES 32, 34, 35, 36, 40**|
|---|---|---|---|
|**30**|Involved|Player ID's in line up|This will show allplayers in the startingline upand available as a substitute|
|**41**|Injury||Substitution,event 18,because of injury|
|**42**|Tactical||Substitution,event 18 for tactical reasons|
|**44**|Player position|_Dynamic_|Goalkeeper, Defender, Midfielder, Forward or Substitute. These are the default / natural<br>positions associated with each player and not necessarily the position they played in the match;<br>seequalifier 131 for this.|
|**59**|Jersey number|Shirt number of<br>player(s)|This will be shown for substitutions, line ups, line up changes|
|**130**|Team formation|Formation ID|See appendix 8|
|**131**|Teamplayer formation|1 to 11|Playerposition within a formation - 'See appendix 8|
|**145**|Formation slot|1 to 11|Formationposition of aplayer comingon - see appendix 8|
|**194**|Captain|Player ID|ID of theplayer who is the team captain|
|**197**|Team kit|Kit ID|Kit of the team|



|**ID**|**Referee**|**Values**|**Description**|
|---|---|---|---|
|**50**|Officialposition|1,2,3,4|Referee,Linesman#1,Linesman#2,Forth official|
|**51**|Official ID|Official ID|Unique ID for the official|
|**200**|Referee stop||Referee stopsplay|
|**201**|Referee delay||Delayinplayinstructed byreferee|
|**208**|Referee Injury||Referee injured|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

14 

|**ID**|**Attendance**|**Values**|**Description**|
|---|---|---|---|
|**49**|Attendance figure|_Dynamic_|Number ofpeople in the crowd|



|**ID**|**Stoppages**|**Values**|**Description - EVENT TYPE 27**|
|---|---|---|---|
|**53**|Injuredplayer id|ID ofplayer injured|ID of theplayer who is injured and causinga delayin thegame|
|**202**|Weatherproblem||Bad weather stops or interruptsplay|
|**203**|Crowd trouble||Trouble within the crowd stops or delaysplay|
|**204**|Fire||Fire with the stadium stops or delaysplay|
|**205**|Object thrown onpitch||Object throw from the crowd lands on thepitch and delaysplay|
|**206**|Spectator onpitch||Spectator comes onto thepitch and forces a delayinplay|
|**207**|Awaitingofficials decision||Given to an event/delaywhere the referee still has to make a decision|
|**208**|Referee injury||Referee sustained injurycausingstoppage inplay|
|**226**|Suspended||Game is has not finished but is suspended|
|**227**|Resume||Game has resumed after beingsuspended mid-waythrough on aprevious date|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

15 

|**ID**<br>**General**|**ID**<br>**General**|**Values**<br>**Description**|**Values**<br>**Description**|
|---|---|---|---|
|**54**|End cause|1,2,3,4,5,6,7,99,100|Golden goal, weather, crowd, insufficient players, floodlight failure, frozen pitch, waterlogged pitch,<br>other,unknown|
|**56**|Zone|Back, left, centre,<br>right|Area on the pitch - see appendix 7|
|**57**|End type||End of the match|
|**127**|Direction of play|Right to Left<br>Left to Right|Event type 32 - Actual direction of play in relation to TV camera. X/Y coordinates however are<br>ALWAYS all normalized to**Left to Right.**|
|**144**|Deleted event type|Event ID|An event which should be removed. Value will show the ID of this event|
|**189**|Player not visible||Broadcast footage showing replay and not live footage – this event is what Opta analysts believe<br>occurred.|
|**209**|Game end||Thegame is finished|
|**211**|Overrun||TAKE ON (3) – where a player takes on an opponent but the ball runs away from them out of play<br>or to an opponent.|
|**229**|Post-match complete||Optapost matchqualitycontrol has been completed on this match|



F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

16 

## **Appendix 3 – useful queries** 

Below is a table that can be used as a guide to calculate some of the more common statistic types from the F24 data: 

|**English**|**type_id**|**outcome**|**qualifier_id**|**Extra info**|**_EXCLUDING_**<br>**_EVENTS WITH_**<br>**_THESE_**<br>**_QUALIFIERS_**|
|---|---|---|---|---|---|
|**passes total**|_1_|_-_|_-_|Include short<br>corners where<br>qualifier 6 is present<br>but notqualifier 2|_2, 5, 6, 107,_<br>_123,124_|
|**Passes successful**|_1_|_1_|_-_||_2, 5, 6, 107,_<br>_123,124_|
|**passes unsuccessful**|_1_|_0_|_-_||_2, 5, 6, 107,_<br>_123,124_|
|**Crosses Total(openplay)**|_1_|_-_|_2_||_5, 6_|
|**Successful Crosses Total**<br>**(open)**|_1_|_1_|_2_||_5, 6_|
|**Unsuccessful Crosses**<br>**Total (excl corners & Free**<br>**kicks)**|_1_|_0_|_2_||_5, 6_|
|**assists total ***|_16_|_1_|_29, 55_|Value of 55 =<br>event_id of the<br>assisting pass||
|**key passes total ***|_13, 14, 15_|_-_|_29, 55_|Value of 55 =<br>event_id of the key<br>pass||
|**offensive passes total**|_1_|_-_||If (x < end_x)|_2, 5, 6, 107,_<br>_123,124_|
|**offensive passes won**|_1_|_1_||If (x < end_x)|_2, 5, 6, 107,_<br>_123,124_|
|**offensive passes lost**|_1_|_0_||If (x < end_x)|_2, 5, 6, 107,_<br>_123,124_|
|**defensive/backward**<br>**passes**|_1_|_-_||If (x > end_x)|_2, 5, 6, 107,_<br>_123,124_|
|**sideway passes total**|_1_|_-_||If (x = end_x)|_2, 5, 6, 107,_<br>_123,124_|
|**long passes total**|_1_|_-_|_1_||_2, 5, 6, 107,_<br>_123,124_|
|**long passes won**|_1_|_1_|_1_||_2, 5, 6, 107,_<br>_123,124_|
|**long passes lost**|_1_|_0_|_1_||_2, 5, 6, 107,_<br>_123,124_|
|**aerial total**|_44_|_-_||||
|**aerial won**|_44_|_1_||||
|**aerial lost**|_44_|_0_||||
|**ground duels total**|_3,4,7,45,54_|_-_||||
|**ground duels won**|_3, 4,7,54_|_1_||||
|**ground duels lost**|_3,_<br>_4,7,45,50_|_0_||||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

17 

|**English**|**type_id**|**outcome**|**qualifier_id**|**Extra info**|**_EXCLUDING_**<br>**_EVENTS WITH_**<br>**_THESE_**<br>**_QUALIFIERS_**|
|---|---|---|---|---|---|
|**Free kicks taken**<br>**total**|_1_|_-_|_5_|||
|**Fouls total**|_4_|_-_||||
|**Fouls won**|_4_|_1_||||
|**Fouls conceded**|_4_|_0_||||
|**handball**<br>**conceded**|_4_|_0_|_10_|||
|**corners total**|_1_|_-_|_6_|Crossed corners include<br>qualifier 2, short corner without<br>qualifier 2||
|**corners into box**<br>**- successful**|_1_|_1_|_6_|If (83 < end_x < 100)<br>If(21 < end_y< 78.9)||
|**corners into box**<br>**- unsuccessful**|_1_|_0_|_6_|If (83 < end_x < 100)<br>If(21 < end_y< 78.9)||
|**interceptions**|_8_|_-_||||
|**tackles won**|_7_|_1 or 0_||Outcome 1 – tackle won and<br>possession won or ball went<br>out of play. Outcome 0 – only<br>tackle won nopossession won||
|**Tackle lost -**<br>**Challenge **|_45_|_0_||||
|**saves total**|_10_|_1_||||
|**Save (block by**<br>**outfielder)**|_10_|_1_|_94_|||
|**Claim (gk**<br>**catches cross)**|_11_|_1_||||
|**clearance won**|_12_|_1_||||
|**clearance lost**|_12_|_0_||||
|**headed**<br>**clearance won**|_12_|_1_|_15_|||
|**headed**<br>**clearance lost**|_12_|_0_|_15_|||
|**Total shots**|_13,14,15,16_|_-_||||
|**shots on target**|_15,16_|_-_|||_82 (blocked_<br>_shots)_|
|**shots off target**|_13,14_|_-_||||
|**Goals**|_16_|_1_||||
|**Goals from**<br>**openplay**|_16_|_1_|_22_|||
|**Goals from set**<br>**plays **|_16_|_1_|_24_|||
|**Goals from**<br>**penalties**|_16_|_1_|_9_|||
|**Own Goals**|_16_|_0_|_28_|Team_id will be the team<br>conceding the own goal||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

18 

|**English**|**type_id**|**outcome**|**qualifier_id**|**Extra info**|**_EXCLUDING_**<br>**_EVENTS WITH_**<br>**_THESE_**<br>**_QUALIFIERS_**|
|---|---|---|---|---|---|
|**headed shots on**<br>**target**|_15,16_|_-_|_15_||_82 (blocked_<br>_shots)_|
|**headed shots**<br>**total**|_13,14,15,16,24_|_-_|_15_|||
|**headed shots off**<br>**target**|_13,14_|_-_|_15_|||
|**shots blocked by**<br>**outfielder**|_15_|_-_|_82_|||
|**Total touches**|_See below**_|_-_||||
|**Successful Take**<br>**on(dribble)**|_3_|_1_||||
|**Unsuccessful**<br>**Take on (dribble)**|_3_|_0_||Qualifier 211 indicates an<br>“overrun” which is not<br>always a duel event.<br>Optional to include these.||
|**Fouls won**|_4_|_1_||||
|**Fouls conceded**|_4_|_0_||||
|**Penalty**<br>**conceded**|_4_|_0_|_9_|||
|**Yellow Card**|_17_|_-_|_31_|||
|**2nd Yellow Cards**|_17_|_-_|_32_|||
|**Red Cards**|_17_|_-_|_33_|||



## ****Touches** 

To calculate all touches, aggregate all events with the following event type ids - _irrespective of qualifiers or outcomes or position_ : 

_2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 41, 42, 50, 52, 54 and 61._ 

Plus all event type id 1 - _except those flagged with qualifier 123._ 

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

19 

## **Appendix 4 – assist and keypass interpretation** 

When `qualifier` **`=”55”`** is present, then look for its corresponding **`value=””`** ; this will show you the value of the **`event_id=””`** to look at to find information. It is basically telling you that the shot on goal was assisted (in this case a ‘keypass’) by a pass and it is telling you where to look to find the pass details. 

## **For example:** 

```
<Eventid="783279345"event_id="170"type_id="1"period_id="1"min="20"
sec="33"player_id="19645"team_id="52"outcome="1"x="98.0"y="65.9"
keypass="1"timestamp="2011-08-13T15:21:16.403"last_modified="2011-08-
13T17:21:17">
```

```
<Qid="1360104517"qualifier_id="140"value="95.7"/>
<Qid="716687577"qualifier_id="154"/>
<Qid="1024698286"qualifier_id="141"value="69.8"/>
<Qid="548528358"qualifier_id="213"value="2.3"/>
<Qid="1464195139"qualifier_id="212"value="3.6"/>
<Qid="811964232"qualifier_id="56"value="Center"/>
<Qid="629946245"qualifier_id="210"/>
```

```
</Event>
```

```
<Eventid="1079282470"event_id="171"type_id="15"period_id="1"
min="20"sec="35"player_id="2019"team_id="52"outcome="1"x="95.7"
y="69.8"timestamp="2011-08-13T15:21:17.559"last_modified="2011-08-
13T17:21:18">
```

- `<Q id=` **`"1372749641"`** `qualifier_id=` **`"76"`** `/> <Q id=` **`"1476860249"`** `qualifier_id=` **`"20"`** `/> <Q id=` **`"607536004"`** `qualifier_id=` **`"102"`** `value=` **`"53.5"`** `/> <Q id=` **`"852431923"`** `qualifier_id=` **`"65"`** `/> <Q id=` **`"951864007"`** `qualifier_id=` **`"154"`** `/> <Q id=` **`"1904271995"`** `qualifier_id=` **`"56"`** `value=` **`"Center"`** `/> <Q id=` **`"995057860"`** `qualifier_id=` **`"103"`** `value=` **`"4.2"`** `/> <Q id=` **`"1206524667"`** `qualifier_id=` **`"146"`** `value=` **`"99.7"`** `/> <Q id=` **`"1896231395"`** `qualifier_id=` **`"22"`** `/> <Q id=` **`"119954813"`** `qualifier_id=` **`"147"`** `value=` **`"53.8"`** `/> <Q id=` **`"432940257"`** `qualifier_id=` **`"29"`** `/> <Q id=` **`"2000327362"`** `qualifier_id=` **`"55"`** `value=` **`"170"`** `/>` 

- `</Event>` 

   - So you can see that the value attribute with **`qualifier_id=”55”`** is telling you to look at **`event_id=”170”`** from the preceding event. 

   - By looking at **`event_id=”170”`** you can see this was a pass ( **`type_id=”1”`** ) and **`qualifier_id=”55”`** tells you that it assisted the shot on goal that was saved ( **`type_id=”15”`** ). 

   - Note that **`keypass=”1”`** indicates a pass that led directly to a shot on goal (but not a goal) and **`assist=”1”`** denotes a pass that led directly to a shot that was a goal. 

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

20 

## **Appendix 5 – the <Event> tag** 

Some of the attributes within the `<Event>` tag can cause confusion when it comes to interpreting their meanings and uses. 

## **An example:** 

```
<Eventid="2044318208"event_id="153"type_id="5"period_id="1"min="19"
sec="31"player_id="49396"team_id="368"outcome="1"x="-2.0"y="53.3"
timestamp="2012-06-23T20:04:45.40"last_modified="2012-06-23T20:04:45">
```

## **Definitions:** 

- `id=` **`"2044318208"`** This is the absolute unique integer that we assign to each individual match event and it can be used to database the event and search at a later date. 

- `event_id=` **`"153"`** This is the reference to the order of the match events _within this match only_ and the count runs simultaneously for each team. For example _(NB in a real F24b match file, the two_ _`event_id`_ _**`=”1”`** attributes are actually the team line-ups, so treat the below example as merely theory for illustrative purposes):_ 

   - Team A’s first match event is a successful pass from player 1 to player 2, so this is `event_id` **`=”1”`** ; the second event is another successful pass from player 2 to player 3, so this is `event_id` **`=”2”`** ; the third event is an unsuccessful pass from player 3 to player 4 as it was intercepted by the opposite team, so the `event_id` count stops at **`“2”`** for Team A (until they get the ball back in possession, at which point their count will start again at **`“3”`** ). Now that Team B have the ball, let’s say there is a successful pass from their player 1 to their player 2, so Team B’s `event_id` count begins at **`“1”`** , then there’s another successful pass from their player 2 to player 3, so this is `event_id` **`=”2”`** … this alternate ascending count continues through the match for both teams as their number of match events increase. 

- `timestamp=` **`"2012-06-23T20:04:45.40"`** This is the timestamp that relates to the date and time that _the event occurred within the match._ 

- `last_modified=` **`"2012-06-23T20:04:45"`** This relates to the time that the event was _last modified by our analysts,_ for example an event could be edited, deleted or a new one inserted. 

***Important note:** whilst at first glance `event_id` looks as though it can be used to order each team’s match events chronologically, there are sometimes cases that after our analysts have reviewed each match, that the `timestamp` of the event can be tweaked. In which case this can knock the `event_id` ’s out of order (eg instead of `event_id` **`=”1”`** , then `event_id` **`=”2”`** and `event_id` **`=”3”`** , it could change to `event_id` **`=”1”`** , then `event_id` **`=”3”`** and `event_id` **`=”2”`** ). 

So please be aware that you should _always order events by the following attributes_ (in this order): 

- `team_id` ; then 

- `period_id` ; then 

- `min` ; then 

- `sec` ; and then 

- `timestamp` . 

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

21 

## **Appendix 6 – how events are deleted** 

An example of a deleted event will look something like this in the feed: 

```
<Eventid="328486810"event_id="26"type_id="43"period_id="1"min="4"
sec="8"player_id="2399"team_id="110"outcome="1"x="0.0"y="0.0"
timestamp="2010-12-04T15:04:17.278"last_modified="2010-12-04T15:04:34">
```

```
<Qid="19756363"qualifier_id="56"value="Back"/>
```

```
<Qid="371368182"qualifier_id="144"value="50"/>
</Event>
```

Where `type_id` **`=”43”`** describes this event as one that has been deleted from the game file. 

`qualifier_id=` **`"144"`** is used to inform you about the type of match action that was deleted, in this case `value=` **`"50"`** describes the deleted event as one that was a ‘dispossession’ event. 

If you database each of the F24 match files that we send as the game progresses, when a deletion occurs, you will be able to search `id` **`=”328486810”`** from the previous F24 files you have received during the game. 

You will then be able to locate the specific event from a previously delivered match file, which would have looked something like this: 

```
<Eventid="328486810"event_id="26"type_id="50"period_id="1"min="3"
sec="37"player_id="2399"team_id="110"outcome="1"x="65.3"y="2.7"
timestamp="2010-12-04T15:03:47.195"last_modified="2010-12-04T15:03:47">
```

```
<Qid="313977382"qualifier_id="56"value="Right"/>
```

```
</Event>
```

* _This can only be achieved if you database each F24 match feed_ as it is delivered live. If not and you allow each F24 match feed to be overwritten with every new delivery, then the only evidence that you will see that there was a deleted event is by the inclusion of the `type_id=` **`"43"`** attribute. 

## **Notes:** 

- Once we delete an event, the associated event’s data will be removed from the feed and so this will only be visible in the feeds that were produced before the event was deleted. 

- The value of the `event_id=` **`""`** attribute remains associated with its deleted event and the ascending count continues to increase in just the same way as if it were any other `type_id` . 

   - So for example, `event_id=` **`"1",`** `event_id=` **`"2"`** and `event_id=` **`"3"`** which could relate to pass, pass and pass might then become; pass, deleted event and pass. 

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

22 

## **Appendix 7 – how events are edited/modified** 

We can edit events either live in-play or during our post-match data verification checks; these can be things such as slight player position changes in formations, or the official time of a goal adjusted by a couple of seconds etc. 

To associate an event as being edited, we make use of the `last_modified` attribute eg: 

```
last_modified="2010-12-04T15:03:47"
```

By using this attribute, it allows you to avoid the situation whereby you’d be faced with having to parse every row of the feed each time a new file is delivered, in an attempt to make sure nothing had been edited. 

Instead, by looking for the `last_modified` attribute’s appearance only, this will allow you to parse just the new events that are delivered each time, safe in the knowledge that until this attribute is flagged up on your parser, that all previous information can be deemed as correct. 

## **Q id** 

Whilst the id associated with the event does not change (eg `Event id=` **`"316446219"`** ) in the occurrence of an edited event, the qualifiers – if modified – will be associated with new id value in the `id` attribute ie `Q id=` **`"212475322"`** 

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

23 

## **Appendix 8 – outcome definitions** 

The below table highlights how to interpret the outcome=”0” and outcome=”1” attributes for their corresponding type_id events: 

|**Event ID**|**Name**|**Outcome 0**|**Outcome 1**|
|---|---|---|---|
|1|Pass|Unsuccessful pass ie pass did<br>not find team mate|Successful pass|
|2|Offside Pass|Always set to "1"||
|3|Take On|Unsuccessful – player lost<br>possession or was tackled|Successful take on|
|4|Foul|Player that was fouled|Player who committed the foul|
|5|Out|The team that put the ball out|The team that therefore gained<br>possession|
|6|Corner Awarded|The team that conceded the<br>corner|The team that won the corner|
|7|Tackle|Unsuccessful attempted<br>tackle/challenge from this team<br>to the team on the ball ie other<br>team retains possession after<br>the challenge|Successful tackle ie challenging<br>player wins possession of the<br>ball from the other team|
|8|Interception|Always set to "1"||
|9|Turnover|n/a||
|10|Save|Always set to "1"||
|11|Claim|Keeper drops the ball after an<br>attempted catch from a cross.<br>The keeper may then pick up<br>the ball again and retain<br>possession, but this would be a<br>separate event|Keeper catches the cross in one<br>attempt ie no drop|
|12|Clearance|Player clears ball from defence<br>but possession switches to<br>other team (not the same as<br>player clearing ball out of play<br>which is outcome="1")|Player clears ball from defence<br>either to another team mate (ie<br>possession retained) or straight<br>out of play|
|13|Miss|Always set to "1"||
|14|Post|Always set to "1"||
|15|Attempt Saved|Always set to "1"||
|16|Goal|Always set to "1"||
|17|Card|Always set to "1"||
|18|Player off|Always set to "1"||
|19|Player on|Always set to "1"||
|20|Player retired|Always set to "1"||
|21|Player returns|Always set to "1"||
|22|Player becomes<br>goalkeeper|Always set to "1"||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

24 

|**Event ID**|**Name**|**Outcome 0**|**Outcome 1**|
|---|---|---|---|
|23|Goalkeeper<br>becomesplayer|Always set to "1"||
|24|Condition change|Always set to "1"||
|25|Official change|Always set to "1"||
|27|Start delay|Always set to "1"||
|28|End delay|Always set to "1"||
|30|End|Always set to "1"||
|32|Start|Always set to "1"||
|34|Team set up|Always set to "1"||
|35|Player changed<br>position|Always set to "1"||
|36|Player changed<br>Jerseynumber|Always set to "1"||
|37|Collection End|Always set to "1"||
|38|Temp_Goal|Always set to "1"||
|39|Temp_Attempt|Always set to "1"||
|40|Formation change|Always set to "1"||
|41|Punch|Always set to "1"||
|42|Good Skill|Always set to "1"||
|43|Deleted event|Always set to "1"||
|44|Aerial|Player lost aerial duel|Player won the aerial duel|
|45|Challenge|Always set to "0" ie a challenge by definition is unsuccessful and<br>the player does not win the ball (by winning the ball this would be a<br>tackle ie type_id="7")||
|47|Rescinded card|Always set to "1"||
|49|Ball recovery|Always set to "1"||
|50|Dispossessed|Always set to "1"||
|52|Keeperpick-up|Always set to "1"||
|53|Cross not claimed|Always set to "1"||
|54|Smother|Always set to "1"||
|55|Offsideprovoked|Always set to "1"||
|51|Error|Always set to "1"||
|56|Shield ball oop|Always set to "1"||
|57|Foul throw in|Always set to "1"||
|58|Penaltyfaced|Always set to "1"||
|59|Keeper Sweeper|Goalkeeper comes off the line<br>and clears ball but possession<br>switches to other team (not the<br>same as player clearing ball out<br>of play which is outcome="1")|Goalkeeper comes off the line<br>and either clears ball to another<br>team mate (ie possession<br>retained) or straight out of play|
|60|Chance missed|Always set to "0"||
|61|Ball touch|Player unsuccessfully controlled<br>the ball ie lost possession|Ball simply hit player<br>unintentionally|
|63|Temp_Save|Always set to "1"||
|64|Resume|Always set to "1"||
|65|CRD|Always set to "1"||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

25 

## **Appendix 9 – associated qualifiers** 

This table shows which qualifiers have appeared with the different event types throughout the production of F24. Whilst this list should not be taken as definitive, it does show the list of qualifiers that could reasonably be expected to appear with associated events. It serves as guidance but it is subject to change as more feeds are produced. 

|**type_id**|**qualifier_id**|
|---|---|
|1|1, 2, 4, 5, 6, 15, 22, 23, 24, 25, 26, 29, 31, 55, 56, 96, 97, 106, 107, 123, 124, 138,<br>140, 141, 154, 155, 156, 157, 160, 168, 195, 196, 198, 199, 210, 212, 213, 214, 218,<br>223, 224, 225|
|2|1, 2, 3, 4, 5, 6, 7, 8, 55, 56, 107, 123, 124, 140, 141|
|3|56, 211|
|4|9, 10, 11, 12, 13, 34, 40, 56, 95, 132, 184|
|5|56|
|6|56, 73, 219, 220, 221, 222|
|7|14, 56, 167|
|8|13, 14, 15, 31, 32, 56|
|9|n/a|
|10|1, 2, 9, 14, 15, 17, 21, 25, 29, 55, 56, 82, 88, 90, 91, 92,93, 94, 101, 102, 103, 137,<br>139, 173, 175, 176, 177, 178, 179, 180, 181, 182, 183, 190|
|11|1, 2, 56, 88|
|12|1, 2, 14, 15, 56, 91, 128, 167, 185|
|13|1, 2, 9, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 55, 56, 60, 61, 62, 63, 64, 65,<br>66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 96,<br>97, 100, 102, 103, 108, 109, 110, 111, 113, 114, 115, 116, 117, 118, 119, 120, 121,<br>133,137,146,147,153,154,160,188,214,215|
|14|5, 9, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 55, 56, 60, 61, 62, 63, 64, 65,<br>66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 81, 96, 97, 102, 103, 108, 109, 111, 113, 114,<br>116, 117, 118, 119, 120, 121, 133, 146, 147, 154, 160, 214, 215|
|15|1, 2, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 55, 56, 60, 61, 62, 63, 64,<br>65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87,<br>96, 97, 100, 101, 102, 103, 108, 109, 110, 111, 113, 114, 115, 116, 117, 118, 119,<br>120, 121, 122, 133, 138, 139, 146, 147, 154, 160, 192, 214, 215|
|16|2, 9, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 40, 55, 56, 60, 61, 62, 63, 64,<br>65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 87, 96,<br>97, 102, 103, 108, 109, 110, 111, 113, 114, 117, 118, 119, 120, 121, 133, 136, 138,<br>146, 147|
|17|10, 11, 12, 13, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 56, 95, 132, 158, 159, 161,<br>162, 163, 164, 165, 166, 171, 172, 184, 191|
|18|41, 42, 44, 55, 59, 83, 227|
|19|41, 42, 44, 55, 59, 145, 227|
|20|n/a|
|21|145|
|22|44|
|23|44|
|24|45,46,47,48,49|



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

26 

|**type_id**|**qualifier_id**|
|---|---|
|25|50, 51|
|27|41, 53, 200, 201, 202, 203, 204, 205, 206, 207, 208|
|28|n/a|
|30|54, 57, 209, 226, 227|
|32|127|
|34|30, 44, 59, 130, 131, 194, 197, 227|
|35|44|
|36|59|
|37|229|
|38|9, 16, 17, 18, 19, 22, 26, 56, 60, 61, 62, 63, 64, 65, 66, 69, 70, 71|
|39|9, 16, 17, 18, 19, 20, 22, 26, 56, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71|
|40|30, 44, 59, 130, 131, 227|
|41|56|
|42|56|
|43|n/a|
|44|9, 13, 55, 56|
|45|31, 56|
|47|13, 31, 32, 33, 34|
|49|14, 56|
|50|56|
|51|169, 170|
|52|n/a|
|53|n/a|
|54|n/a|
|55|n/a|
|56|56|
|57|56|
|58|9, 56, 73, 75, 138, 178, 179, 186, 187, 188|
|59|56|
|60|55, 56, 154|
|61|56, 138, 228|
|63|56, 173, 178, 182|
|64|n/a|
|65|None availableyet - new stat in 2012/13|



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

27 

## **Appendix 10 – period ID list** 

Below are the period ID values that appear with the period=”” attribute in the <Event> tag: 

|**Period**|**Period_id**|
|---|---|
|Pregame|15|
|Pre match|16|
|Postgame|14|
|First half|1|
|First half ends|10|
|Second half|2|
|Second half ends|11|
|Firstperiod of extra time|3|
|Firstperiod of extra time ends|12|
|Secondperiod of extra time|4|
|Secondperiod of extra time ends|13|
|Penaltyshoot out|5|



## **Appendix 11 – pitch co-ordinates and direction of play** 

This is based on the direction of attack always being from left to right on the x-axis, regardless of the team or period of the game, the defending goal line is always where x=0 and the attacking where x=100. All measurements for events given in the feed should therefore be taken in relation to percentages. 

**==> picture [12 x 246] intentionally omitted <==**

**==> picture [445 x 276] intentionally omitted <==**

**----- Start of picture text -----**<br>
0, 100  100, 100<br>0, 78.9  17, 78.9  83, 78.9  100, 78.9<br>5.8, 63.2  94.2, 63.2<br>50, 50<br>11.5, 50  88.5, 50<br>5.8, 36.8  94.2, 36.8<br>0, 21.1  17, 21.1  83, 21.1  100, 21.1<br>0, 0  100, 0<br>**----- End of picture text -----**<br>


**==> picture [352 x 12] intentionally omitted <==**

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

28 

## **Appendix 12 – goalmouth co-ordinates** 

**==> picture [455 x 318] intentionally omitted <==**

**----- Start of picture text -----**<br>
 100   100<br> 60.0   60.0<br> 42.0<br> 40.0   40.0<br> 38.0<br> 20.0<br> 59.3   55.8   54.8   51.8   48.2   45.2   44.2   40.7<br>**----- End of picture text -----**<br>


**EVENT - Goal, Attempt Saved:** 

|**Qualifier**|**end_y**||**end_z **|
|---|---|---|---|
|Low Left|(51.8 <= end_y<= 54.8)||(0 <= end_z <= 20)|
|High Left|(51.8 <= end_y<= 54.8)||(20 <= end_z <= 38)|
|Low Centre|(48.2 <= end_y<= 51.8)||(0 <= end_z <= 20)|
|High Centre|(48.2 <= end_y<= 51.8)||(20 <= end_z <= 38)|
|Low Right|(45.2 <= end_y<= 48.2)||(0 <= end_z <= 20)|
|High Right|(45.2 <= end_y<= 48.2)||(20 <= end_z <= 38)|
||**EVENT - Post:**|||
|**Qualifier**|**end_y**||**end_z **|
|Left|(54.8 <= end_y<= 55.8)||(0 <= end_z <= 38)|
|High|(44.2 <= end_y<= 55.8)||(38 <= end_z <= 42)|
|Right|(44.2 <= end_y<= 45.2)||(0 <= end_z <= 38)|
||**EVENT - Miss:**|||
|**Qualifier**|**end_y**||**end_z **|
|Close Left|(55.8 <= end_y<= 59.3)||(0 <= end_z <= 40)|
|Close High Left|(55.8 <= end_y<= 59.3)||(40 <= end_z <= 60)|
|Close Right|(40.7 <= end_y<= 44.2)||(0 <= end_z <= 40)|
|Close High Right|(40.7 <= end_y<= 44.2)||(40 <= end_z <= 60)|
|Close High|(44.2 <= end_y<= 55.8)||(42 <= end_z <= 60)|
|Left|(59.3 <= end_y<= 100)||(0 <= end_z <= 40)|
|Right|(0 <= end_y<= 40.7)||(0 <= end_z <= 40)|
|HighLeft|(55.8 <= end_y<= 100)||(60 <= end_z <= 100)|
|HighRight|(0 <= end_y<= 44.2)||(60 <= end_z <= 100)|
|High|(44.2 <= end_y<= 55.8)||(60 <= end_z <= 100)|



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

29 

## **Appendix 13 – pitch zones** 

When Qualifier 56 is shown with an event it will also display a value which can be right, left, centre or back. The diagram below highlights what these zones are on the pitch. 

**==> picture [450 x 280] intentionally omitted <==**

**----- Start of picture text -----**<br>
Right Zone<br>Back<br>Centre Zone<br>Zone<br>Left Zone<br>**----- End of picture text -----**<br>


Qualifiers 16, 17, 18, 19 and 60 - 71 refer to areas of the pitch. The below diagram illustrates where these zones are. 

**==> picture [451 x 263] intentionally omitted <==**

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

30 

## **Appendix 14 - playing positions** 

When Event 34 is shown it will include Qualifier 30, 130 and 131. 

- 130 will indicate the formation the team will be playing in 

- 30 will list the players 

- 131 will list the playing positions 

The order that the players are listed in qualifier 30 will be the same order as the positions listed on qualifier 131. For example: 

```
<Qid="1998281501"qualifier_id="130"value="8"/>
```

```
<Qid="193244804"qualifier_id="30"value="59936, 37748, 42427, 8758,
17127, 51507, 20467, 21091, 12297, 41792, 43274, 8597, 57214, 81880, 37096,
13227, 56861, 15675"/>
```

```
<Qid="280405493"qualifier_id="131"value="1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
11, 0, 0, 0, 0, 0, 0, 0"/>
```

With regards to the qualifier id 130 (ie formation), this can be interpreted as the team playing in a 4231 formation which is depicted below from formation number 8. 

For line ups using qualifier id’s 130 and 131 in conjunction, you can see for example that position 1 will be player 59936 and position 7 will be 20467. Where position = 0, this relates to a substitute for which we do not current record the exact playing position. 

The diagrams overleaf show all of the possible formation numbers and the layout of players in this formation – _note that team formation #1 is not used._ 

**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

31 

## **Player Layout** 

The players are laid out in right to left, defense to forwards. Therefore if a team has been assigned a 442 formation; the player tagged 2 will be right back, 3 right centre back, 4 left centre  back, 5 left back, 6 right midfield, 7 right centre midfield, 8 left centre midfield, 9 left midfield, 10 right centre forward, 11 left centre forward. 

**Team Formation 2 – 442:** 

|||**1**|**1**|||
|---|---|---|---|---|---|
|**2**|**5**||**6**||**3**|
|**7**|**4**||**8**||**11**|
||**10**||**9**|||



## **Team Formation 3 – 41212 (Diamond):** 

|||**1**|**1**|||
|---|---|---|---|---|---|
|**2**|**5**||**6**||**3**|
|||**4**||||
|**7**|||||**11**|
|||**8**||||
||**10**||**9**|||



## **Team Formation 4 – 433:** 

|||**1**|**1**|||
|---|---|---|---|---|---|
|**2**||**5**|**6**||**3**|
|**7**||**4**||**8**||
|**10**||**9**||**11**||



## **Team Formation 5 – 451:** 

|||**1**|**1**|||||
|---|---|---|---|---|---|---|---|
|**2**|**5**|||**6**|||3|
|**7**|**4**|||**8**|11|||
|||**10**||||||
|||**9**||||||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

32 

**Team Formation 6 – 4411:** 

|||**1**|**1**|**1**||
|---|---|---|---|---|---|
|**2**||**5**|**6**||**3**|
|**7**||**4**|**8**||**11**|
|||**10**||||
|||**9**||||



**Team Formation 7 – 4141:** 

|||**1**|**1**|**1**||
|---|---|---|---|---|---|
|**2**||**5**|**6**||3|
|||**4**||||
|**7**||**8**|**10**||11|
|||**9**||||



**Team Formation 8 – 4231:** 

||||**1**|**1**|**1**|**1**||||
|---|---|---|---|---|---|---|---|---|---|
|**2**|||**5**||**6**|||**3**||
||||**8**||**4**|||||
||**7**|||**10**|||**11**|||
||||**9**|||||||



**Team Formation 9 – 4321:** 

||||**1**|**1**|**1**|**1**||||
|---|---|---|---|---|---|---|---|---|---|
|**2**|||**5**||**6**|||**3**||
||**8**|||**4**|||**7**|||
||||**10**||**11**|||||
||||**9**|||||||



**Team Formation 10 – 532:** 

||||**1**|**1**|**1**|**1**||||
|---|---|---|---|---|---|---|---|---|---|
|**2**||**6**||**5**||**4**|||**3**|
|||**7**||**8**||**11**||||
|||**10**|||**9**|||||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

33 

**Team Formation 11 – 541:** 

||||**1**|**1**|**1**|**1**||||
|---|---|---|---|---|---|---|---|---|---|
|**2**||**6**||**5**|||**4**|**3**||
||**7**||**8**||**10**||**11**|||
||||**9**|||||||



## **Team Formation 12 – 352:** 

||||||**1**|**1**|**1**|**1**||||||
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|||**6**||**5**|||||||**4**|||
|**2**|||**7**||||**8**|||||**3**||
|||||||**11**||||||||
||||**10**||||**9**|||||||



**Team Formation 13 – 343:** 

|||||**1**|**1**|||||
|---|---|---|---|---|---|---|---|---|---|
||**6**|||**5**||**4**||||
|**2**||**7**||||**8**|||**3**|
||**10**|||**9**||**11**||||



**Team Formation 14 – 31312** 

||||**1**|**1**|**1**|**1**||||
|---|---|---|---|---|---|---|---|---|---|
|||**6**||**5**||**7**||||
||||**4**|||||||
|||**2**||**8**||**3**||||
||||**10**|||||||
|||**9**|||**11**|||||



**Team Formation 15 – 4222:** 

||**1**|**1**||
|---|---|---|---|
|**2**|**5**|**6**|**3**|
||**4**|**7**||
||**8**|**11**||
||**10**|**9**||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

34 

## **Team Formation 16 – 3511:** 

||||||**1**|**1**||||||
|---|---|---|---|---|---|---|---|---|---|---|---|
|||**6**|||**5**||||**4**|||
|**2**||**7**|||||**8**|||**3**||
||||||**11**|||||||
||||||**10**|||||||
||||||**9**|||||||



## **Team Formation 17 – 3421:** 

|||||**1**|**1**|**1**|**1**|**1**|||||
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|||**6**|||**5**||||**4**||||
|**2**||**7**|||||||**8**||**3**||
||**10**||||||||**9**||||
|||||**11**|||||||||



## **Team Formation 18 – 3412:** 

||||**1**|**1**|**1**|||||||
|---|---|---|---|---|---|---|---|---|---|---|---|
|||**6**||**5**|||**4**|||||
|**2**||**7**||||**8**|||||**3**|
|||||||**9**||||||
||**10**|||||**11**||||||



**==> picture [86 x 33] intentionally omitted <==**

F24: Feed appendices document | **Erro! Não existe nenhum texto com o estilo especificado no documento.** 

