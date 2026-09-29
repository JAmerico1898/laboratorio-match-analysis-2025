#%%
#Training xA model (action-based Expected Assists) on Premier League data
"""Train action-based Expected Assists models on PL possession chains.
Step 1: GradientBoostingClassifier to predict P(pass assists a shot)
Step 2: LinearRegression to predict E[xG | assist]
Models are saved for use on Brasileirão data."""

import pandas as pd
import numpy as np
import json
import os
import pathlib
import warnings
from itertools import combinations_with_replacement
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from joblib import dump
import statsmodels.api as sm
import statsmodels.formula.api as smf

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

#%%
# Loading PL training data
"""Load all 380 PL match JSONs from xG_Training_data/."""

game_ids = [
1575781, 1575782, 1575783, 1575784, 1575785, 1575786, 1575787, 1575788,
1575789, 1575790, 1575791, 1575792, 1575793, 1575794, 1575795, 1575796,
1575797, 1575798, 1575799, 1575800, 1575801, 1575802, 1575803, 1575804,
1575805, 1575806, 1575807, 1575808, 1575809, 1575810, 1575811, 1575812,
1575813, 1575814, 1575815, 1575816, 1575817, 1575818, 1575819, 1575820,
1575821, 1575822, 1575823, 1575824, 1575825, 1575826, 1575827, 1575828,
1575829, 1575830, 1575831, 1575832, 1575833, 1575834, 1575835, 1575836,
1575837, 1575838, 1575839, 1575840, 1575841, 1575842, 1575843, 1575844,
1575845, 1575846, 1575847, 1575848, 1575849, 1575850, 1575851, 1575852,
1575853, 1575854, 1575855, 1575856, 1575857, 1575858, 1575859, 1575860,
1575861, 1575862, 1575863, 1575864, 1575865, 1575866, 1575867, 1575868,
1575869, 1575870, 1575871, 1575872, 1575873, 1575874, 1575875, 1575876,
1575877, 1575878, 1575879, 1575880, 1575881, 1575882, 1575883, 1575884,
1575885, 1575886, 1575887, 1575888, 1575889, 1575890, 1575891, 1575892,
1575893, 1575894, 1575895, 1575896, 1575897, 1575898, 1575899, 1575900,
1575901, 1575902, 1575903, 1575904, 1575905, 1575906, 1575907, 1575908,
1575909, 1575910, 1575911, 1575912, 1575913, 1575914, 1575915, 1575916,
1575917, 1575918, 1575919, 1575920, 1575921, 1575922, 1575923, 1575924,
1575925, 1575926, 1575927, 1575928, 1575929, 1575930, 1575931, 1575932,
1575933, 1575934, 1575935, 1575936, 1575937, 1575938, 1575939, 1575940,
1575941, 1575942, 1575943, 1575944, 1575945, 1575946, 1575947, 1575948,
1575949, 1575950, 1575951, 1575952, 1575953, 1575954, 1575955, 1575956,
1575957, 1575958, 1575959, 1575960, 1575961, 1575962, 1575963, 1575964,
1575965, 1575966, 1575967, 1575968, 1575969, 1575970, 1575971, 1575972,
1575973, 1575974, 1575975, 1575976, 1575977, 1575978, 1575979, 1575980,
1575981, 1575982, 1575983, 1575984, 1575985, 1575986, 1575987, 1575988,
1575989, 1575990, 1575991, 1575992, 1575993, 1575994, 1575995, 1575996,
1575997, 1575998, 1575999, 1576000, 1576001, 1576002, 1576003, 1576004,
1576005, 1576006, 1576007, 1576008, 1576009, 1576010, 1576011, 1576012,
1576013, 1576014, 1576015, 1576016, 1576017, 1576018, 1576019, 1576020,
1576021, 1576022, 1576023, 1576024, 1576025, 1576026, 1576027, 1576028,
1576029, 1576030, 1576031, 1576032, 1576033, 1576034, 1576035, 1576036,
1576037, 1576038, 1576039, 1576040, 1576041, 1576042, 1576043, 1576044,
1576045, 1576046, 1576047, 1576048, 1576049, 1576050, 1576051, 1576052,
1576053, 1576054, 1576055, 1576056, 1576057, 1576058, 1576059, 1576060,
1576061, 1576062, 1576063, 1576064, 1576065, 1576066, 1576067, 1576068,
1576069, 1576070, 1576071, 1576072, 1576073, 1576074, 1576075, 1576076,
1576077, 1576078, 1576079, 1576080, 1576081, 1576082, 1576083, 1576084,
1576085, 1576086, 1576087, 1576088, 1576089, 1576090, 1576091, 1576092,
1576093, 1576094, 1576095, 1576096, 1576097, 1576098, 1576099, 1576100,
1576101, 1576102, 1576103, 1576104, 1576105, 1576106, 1576107, 1576108,
1576109, 1576110, 1576111, 1576112, 1576113, 1576114, 1576115, 1576116,
1576117, 1576118, 1576119, 1576120, 1576121, 1576122, 1576123, 1576124,
1576125, 1576126, 1576127, 1576128, 1576129, 1576130, 1576131, 1576132,
1576133, 1576134, 1576135, 1576136, 1576137, 1576138, 1576139, 1576140,
1576141, 1576142, 1576143, 1576144, 1576145, 1576146, 1576147, 1576148,
1576149, 1576150, 1576151, 1576152, 1576153, 1576154, 1576155, 1576156,
1576157, 1576158, 1576159, 1576160,
1557324, 1557325, 1557326, 1557327, 1557328, 1557329, 1557330, 1557331,
1557332, 1557333, 1557334, 1557335, 1557336, 1557337, 1557338, 1557339,
1557340, 1557341, 1557342, 1557343, 1557344, 1557345, 1557346, 1557347,
1557348, 1557349, 1557350, 1557351, 1557352, 1557353, 1557354, 1557355,
1557356, 1557357, 1557358, 1557359, 1557360, 1557361, 1557362, 1557363,
1557364, 1557365, 1557366, 1557367, 1557368, 1557369, 1557370, 1557371,
1557372, 1557373, 1557374, 1557375, 1557376, 1557377, 1557378, 1557379,
1557380, 1557381, 1557382, 1557383, 1557384, 1557385, 1557386, 1557387,
1557388, 1557389, 1557390, 1557391, 1557392, 1557393, 1557394, 1557395,
1557396, 1557397, 1557398, 1557399, 1557400, 1557401, 1557402, 1557403,
1557404, 1557405, 1557406, 1557407, 1557408, 1557409, 1557410, 1557411,
1557412, 1557413, 1557414, 1557415, 1557416, 1557417, 1557418, 1557419,
1557420, 1557421, 1557422, 1557423, 1557424, 1557425, 1557426, 1557427,
1557428, 1557429, 1557430, 1557431, 1557432, 1557433, 1557434, 1557435,
1557436, 1557437, 1557438, 1557439, 1557440, 1557441, 1557442, 1557443,
1557444, 1557445, 1557446, 1557447, 1557448, 1557449, 1557450, 1557451,
1557452, 1557453, 1557454, 1557455, 1557456, 1557457, 1557458, 1557459,
1557460, 1557461, 1557462, 1557463, 1557464, 1557465, 1557466, 1557467,
1557468, 1557469, 1557470, 1557471, 1557472, 1557473, 1557474, 1557475,
1557476, 1557477, 1557478, 1557479, 1557480, 1557481, 1557482, 1557483,
1557484, 1557485, 1557486, 1557487, 1557488, 1557489, 1557490, 1557491,
1557492, 1557493, 1557494, 1557495, 1557496, 1557497, 1557498, 1557499,
1557500, 1557501, 1557502, 1557503, 1557504, 1557505, 1557506, 1557507,
1557508, 1557509, 1557510, 1557511, 1557512, 1557513, 1557514, 1557515,
1557516, 1557517, 1557518, 1557519, 1557520, 1557521, 1557522, 1557523,
1557524, 1557525, 1557526, 1557527, 1557528, 1557529, 1557530, 1557531,
1557532, 1557533, 1557534, 1557535, 1557536, 1557537, 1557538, 1557539,
1557540, 1557541, 1557542, 1557543, 1557544, 1557545, 1557546, 1557547,
1557548, 1557549, 1557550, 1557551, 1557552, 1557553, 1557554, 1557555,
1557556, 1557557, 1557558, 1557559, 1557560, 1557561, 1557562, 1557563,
1557564, 1557565, 1557566, 1557567, 1557568, 1557569, 1557570, 1557571,
1557572, 1557573, 1557574, 1557575, 1557576, 1557577, 1557578, 1557579,
1557580, 1557581, 1557582, 1557583, 1557584, 1557585, 1557586, 1557587,
1557588, 1557589, 1557590, 1557591, 1557592, 1557593, 1557594, 1557595,
1557596, 1557597, 1557598, 1557599, 1557600, 1557601, 1557602, 1557603,
1557604, 1557605, 1557606, 1557607, 1557608, 1557609, 1557610, 1557611,
1557612, 1557613, 1557614, 1557615, 1557616, 1557617, 1557618, 1557619,
1557620, 1557621, 1557622, 1557623, 1557624, 1557625, 1557626, 1557627,
1557628, 1557629,
1558305, 1558306, 1558307, 1558308, 1558309, 1558310, 1558311, 1558312,
1558313, 1558314, 1558315, 1558316, 1558317, 1558318, 1558319, 1558320,
1558321, 1558322, 1558323, 1558324, 1558325, 1558326, 1558327, 1558328,
1558329, 1558330, 1558331, 1558332, 1558333, 1558334, 1558335, 1558336,
1558337, 1558338, 1558339, 1558340, 1558341, 1558342, 1558343, 1558344,
1558345, 1558346, 1558347, 1558348, 1558349, 1558350, 1558351, 1558352,
1558353, 1558354, 1558355, 1558356, 1558357, 1558358, 1558359, 1558360,
1558361, 1558362, 1558363, 1558364, 1558365, 1558366, 1558367, 1558368,
1558369, 1558370, 1558371, 1558372, 1558373, 1558374, 1558375, 1558376,
1558377, 1558378, 1558379, 1558380, 1558381, 1558382, 1558383, 1558384,
1558385, 1558386, 1558387, 1558388, 1558389, 1558390, 1558391, 1558392,
1558393, 1558394, 1558395, 1558396, 1558397, 1558398, 1558399, 1558400,
1558401, 1558402, 1558403, 1558404, 1558405, 1558406, 1558407, 1558408,
1558409, 1558410, 1558411, 1558412, 1558413, 1558414, 1558415, 1558416,
1558417, 1558418, 1558419, 1558420, 1558421, 1558422, 1558423, 1558424,
1558425, 1558426, 1558427, 1558428, 1558429, 1558430, 1558431, 1558432,
1558433, 1558434, 1558435, 1558436, 1558437, 1558438, 1558439, 1558440,
1558441, 1558442, 1558443, 1558444, 1558445, 1558446, 1558447, 1558448,
1558449, 1558450, 1558451, 1558452, 1558453, 1558454, 1558455, 1558456,
1558457, 1558458, 1558459, 1558460, 1558461, 1558462, 1558463, 1558464,
1558465, 1558466, 1558467, 1558468, 1558469, 1558470, 1558471, 1558472,
1558473, 1558474, 1558475, 1558476, 1558477, 1558478, 1558479, 1558480,
1558481, 1558482, 1558483, 1558484, 1558485, 1558486, 1558487, 1558488,
1558489, 1558490, 1558491, 1558492, 1558493, 1558494, 1558495, 1558496,
1558497, 1558498, 1558499, 1558500, 1558501, 1558502, 1558503, 1558504,
1558505, 1558506, 1558507, 1558508, 1558509, 1558510, 1558511, 1558512,
1558513, 1558514, 1558515, 1558516, 1558517, 1558518, 1558519, 1558520,
1558521, 1558522, 1558523, 1558524, 1558525, 1558526, 1558527, 1558528,
1558529, 1558530, 1558531, 1558532, 1558533, 1558534, 1558535, 1558536,
1558537, 1558538, 1558539, 1558540, 1558541, 1558542, 1558543, 1558544,
1558545, 1558546, 1558547, 1558548, 1558549, 1558550, 1558551, 1558552,
1558553, 1558554, 1558555, 1558556, 1558557, 1558558, 1558559, 1558560,
1558561, 1558562, 1558563, 1558564, 1558565, 1558566, 1558567, 1558568,
1558569, 1558570, 1558571, 1558572, 1558573, 1558574, 1558575, 1558576,
1558577, 1558578, 1558579, 1558580, 1558581, 1558582, 1558583, 1558584,
1558585, 1558586, 1558587, 1558588, 1558589, 1558590, 1558591, 1558592,
1558593, 1558594, 1558595, 1558596, 1558597, 1558598, 1558599, 1558600,
1558601, 1558602, 1558603, 1558604, 1558605, 1558606, 1558607, 1558608,
1558609, 1558610, 1558611, 1558612, 1558613, 1558614, 1558615, 1558616,
1558617, 1558618, 1558619, 1558620, 1558621, 1558622, 1558623, 1558624,
1558625, 1558626, 1558627, 1558628, 1558629, 1558630, 1558631, 1558632,
1558633, 1558634, 1558635, 1558636, 1558637, 1558638, 1558639, 1558640,
1558641, 1558642, 1558643, 1558644, 1558645, 1558646, 1558647, 1558648,
1558649, 1558650, 1558651, 1558652, 1558653, 1558654, 1558655, 1558656,
1558657, 1558658, 1558659, 1558660, 1558661, 1558662, 1558663, 1558664,
1558665, 1558666, 1558667, 1558668, 1558669, 1558670, 1558671, 1558672,
1558673, 1558674, 1558675, 1558676, 1558677, 1558678, 1558679, 1558680,
1558681, 1558682, 1558683, 1558684,
1549539, 1549540, 1549541, 1549542, 1549543, 1549544, 1549545, 1549546,
1549547, 1549548, 1549549, 1549550, 1549551, 1549552, 1549553, 1549554,
1549555, 1549556, 1549557, 1549558, 1549559, 1549560, 1549561, 1549562,
1549563, 1549564, 1549565, 1549566, 1549567, 1549568, 1549569, 1549570,
1549571, 1549572, 1549573, 1549574, 1549575, 1549576, 1549577, 1549578,
1549579, 1549580, 1549581, 1549582, 1549583, 1549584, 1549585, 1549586,
1549587, 1549588, 1549589, 1549590, 1549591, 1549592, 1549593, 1549594,
1549595, 1549596, 1549597, 1549598, 1549599, 1549600, 1549601, 1549602,
1549603, 1549604, 1549605, 1549606, 1549607, 1549608, 1549609, 1549610,
1549611, 1549612, 1549613, 1549614, 1549615, 1549616, 1549617, 1549618,
1549619, 1549620, 1549621, 1549622, 1549623, 1549624, 1549625, 1549626,
1549627, 1549628, 1549629, 1549630, 1549631, 1549632, 1549633, 1549634,
1549635, 1549636, 1549637, 1549638, 1549639, 1549640, 1549641, 1549642,
1549643, 1549644, 1549645, 1549646, 1549647, 1549648, 1549649, 1549650,
1549651, 1549652, 1549653, 1549654, 1549655, 1549656, 1549657, 1549658,
1549659, 1549660, 1549661, 1549662, 1549663, 1549664, 1549665, 1549666,
1549667, 1549668, 1549669, 1549670, 1549671, 1549672, 1549673, 1549674,
1549675, 1549676, 1549677, 1549678, 1549679, 1549680, 1549681, 1549682,
1549683, 1549684, 1549685, 1549686, 1549687, 1549688, 1549689, 1549690,
1549691, 1549692, 1549693, 1549694, 1549695, 1549696, 1549697, 1549698,
1549699, 1549700, 1549701, 1549702, 1549703, 1549704, 1549705, 1549706,
1549707, 1549708, 1549709, 1549710, 1549711, 1549712, 1549713, 1549714,
1549715, 1549716, 1549717, 1549718, 1549719, 1549720, 1549721, 1549722,
1549723, 1549724, 1549725, 1549726, 1549727, 1549728, 1549729, 1549730,
1549731, 1549732, 1549733, 1549734, 1549735, 1549736, 1549737, 1549738,
1549739, 1549740, 1549741, 1549742, 1549743, 1549744, 1549745, 1549746,
1549747, 1549748, 1549749, 1549750, 1549751, 1549752, 1549753, 1549754,
1549755, 1549756, 1549757, 1549758, 1549759, 1549760, 1549761, 1549762,
1549763, 1549764, 1549765, 1549766, 1549767, 1549768, 1549769, 1549770,
1549771, 1549772, 1549773, 1549774, 1549775, 1549776, 1549777, 1549778,
1549779, 1549780, 1549781, 1549782, 1549783, 1549784, 1549785, 1549786,
1549787, 1549788, 1549789, 1549790, 1549791, 1549792, 1549793, 1549794,
1549795, 1549796, 1549797, 1549798, 1549799, 1549800, 1549801, 1549802,
1549803, 1549804, 1549805, 1549806, 1549807, 1549808, 1549809, 1549810,
1549811, 1549812, 1549813, 1549814, 1549815, 1549816, 1549817, 1549818,
1549819, 1549820, 1549821, 1549822, 1549823, 1549824, 1549825, 1549826,
1549827, 1549828, 1549829, 1549830, 1549831, 1549832, 1549833, 1549834,
1549835, 1549836, 1549837, 1549838, 1549839, 1549840, 1549841, 1549842,
1549843, 1549844, 1549845, 1549846, 1549847, 1549848, 1549849, 1549850,
1549851, 1549852, 1549853, 1549854, 1549855, 1549856, 1549857, 1549858,
1549859, 1549860, 1549861, 1549862, 1549863, 1549864, 1549865, 1549866,
1549867, 1549868, 1549869, 1549870, 1549871, 1549872, 1549873, 1549874,
1549875, 1549876, 1549877, 1549878, 1549879, 1549880, 1549881, 1549882,
1549883, 1549884, 1549885, 1549886, 1549887, 1549888, 1549889, 1549890,
1549891, 1549892, 1549893, 1549894, 1549895, 1549896, 1549897, 1549898,
1549899, 1549900, 1549901, 1549902, 1549903, 1549904, 1549905, 1549906,
1549907, 1549908, 1549909, 1549910, 1549911, 1549912, 1549913, 1549914,
1549915, 1549916, 1549917, 1549918,
1491953, 1491954, 1491955, 1491956, 1491957, 1491958, 1491959, 1491960,
1491961, 1491962, 1491963, 1491964, 1491965, 1491966, 1491967, 1491968,
1491969, 1491970, 1491971, 1491972, 1491973, 1491974, 1491975, 1491976,
1491977, 1491978, 1491979, 1491980, 1491981, 1491982, 1491983, 1491984,
1491985, 1491986, 1491987, 1491988, 1491989, 1491990, 1491991, 1491992,
1491993, 1491994, 1491995, 1491996, 1491997, 1491998, 1491999, 1492000,
1492001, 1492002, 1492003, 1492004, 1492005, 1492006, 1492007, 1492008,
1492009, 1492010, 1492011, 1492012, 1492013, 1492014, 1492015, 1492016,
1492017, 1492018, 1492019, 1492020, 1492021, 1492022, 1492023, 1492024,
1492025, 1492026, 1492027, 1492028, 1492029, 1492030, 1492031, 1492032,
1492033, 1492034, 1492035, 1492036, 1492037, 1492038, 1492039, 1492040,
1492041, 1492042, 1492043, 1492044, 1492045, 1492046, 1492047, 1492048,
1492049, 1492050, 1492051, 1492052, 1492053, 1492054, 1492055, 1492056,
1492057, 1492058, 1492059, 1492060, 1492061, 1492062, 1492063, 1492064,
1492065, 1492066, 1492067, 1492068, 1492069, 1492070, 1492071, 1492072,
1492073, 1492074, 1492075, 1492076, 1492077, 1492078, 1492079, 1492080,
1492081, 1492082, 1492083, 1492084, 1492085, 1492086, 1492087, 1492088,
1492089, 1492090, 1492091, 1492092, 1492093, 1492094, 1492095, 1492096,
1492097, 1492098, 1492099, 1492100, 1492101, 1492102, 1492103, 1492104,
1492105, 1492106, 1492107, 1492108, 1492109, 1492110, 1492111, 1492112,
1492113, 1492114, 1492115, 1492116, 1492117, 1492118, 1492119, 1492120,
1492121, 1492122, 1492123, 1492124, 1492125, 1492126, 1492127, 1492128,
1492129, 1492130, 1492131, 1492132, 1492133, 1492134, 1492135, 1492136,
1492137, 1492138, 1492139, 1492140, 1492141, 1492142, 1492143, 1492144,
1492145, 1492146, 1492147, 1492148, 1492149, 1492150, 1492151, 1492152,
1492153, 1492154, 1492155, 1492156, 1492157, 1492158, 1492159, 1492160,
1492161, 1492162, 1492163, 1492164, 1492165, 1492166, 1492167, 1492168,
1492169, 1492170, 1492171, 1492172, 1492173, 1492174, 1492175, 1492176,
1492177, 1492178, 1492179, 1492180, 1492181, 1492182, 1492183, 1492184,
1492185, 1492186, 1492187, 1492188, 1492189, 1492190, 1492191, 1492192,
1492193, 1492194, 1492195, 1492196, 1492197, 1492198, 1492199, 1492200,
1492201, 1492202, 1492203, 1492204, 1492205, 1492206, 1492207, 1492208,
1492209, 1492210, 1492211, 1492212, 1492213, 1492214, 1492215, 1492216,
1492217, 1492218, 1492219, 1492220, 1492221, 1492222, 1492223, 1492224,
1492225, 1492226, 1492227, 1492228, 1492229, 1492230, 1492231, 1492232,
1492233, 1492234, 1492235, 1492236, 1492237, 1492238, 1492239, 1492240,
1492241, 1492242, 1492243, 1492244, 1492245, 1492246, 1492247, 1492248,
1492249, 1492250, 1492251, 1492252, 1492253, 1492254, 1492255, 1492256,
1492257, 1492258, 1492259, 1492260, 1492261, 1492262, 1492263, 1492264,
1492265, 1492266, 1492267, 1492268, 1492269, 1492270, 1492271, 1492272,
1492273, 1492274, 1492275, 1492276, 1492277, 1492278, 1492279, 1492280,
1492281, 1492282, 1492283, 1492284, 1492285, 1492286, 1492287, 1492288,
1492289, 1492290, 1492291, 1492292, 1492293, 1492294, 1492295, 1492296,
1492297, 1492298, 1492299, 1492300, 1492301, 1492302, 1492303, 1492304,
1492305, 1492306, 1492307, 1492308, 1492309, 1492310, 1492311, 1492312,
1492313, 1492314, 1492315, 1492316, 1492317, 1492318, 1492319, 1492320,
1492321, 1492322, 1492323, 1492324, 1492325, 1492326, 1492327, 1492328,
1492329, 1492330, 1492331, 1492332
]

dfs = []
base_path = os.path.join(str(pathlib.Path().resolve()), "xG_Training_data")

for game_id in game_ids:
    path = os.path.join(base_path, f"{game_id}.json")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    temp_df = pd.json_normalize(data["events"], sep="_")
    temp_df["game_id"] = game_id
    dfs.append(temp_df)

df = pd.concat(dfs, ignore_index=True)
df = df.reset_index()
print(f"Loaded {len(dfs)} PL matches, {len(df)} events")

#%%
# Preparing data
"""Same pipeline as possession_chain.py: filter admin events, lost aerials,
corners, goalkeeper events. Mark kickedOut and chain boundaries."""

def _is_dead_ball_restart(qualifiers):
    if not isinstance(qualifiers, list):
        return False
    return any(q["type"]["value"] in (5, 107) for q in qualifiers)

next_event = df.shift(-1, fill_value=0)
df["nextEvent"] = next_event["type_displayName"]

df["kickedOut"] = (
    (next_event["type_value"] == 6) |
    next_event["qualifiers"].apply(_is_dead_ball_restart)
).astype(int)

# force chain break at half-time and game boundaries
boundary = (df["game_id"] != next_event["game_id"]) | (df["period_value"] != next_event["period_value"])
df.loc[boundary, "kickedOut"] = 1
df.loc[boundary, "nextEvent"] = None

# drop non-ball admin events
admin_events = df.loc[df["type_displayName"].isin([
    "Start", "End", "FormationSet", "FormationChange",
    "Card", "SubstitutionOff", "SubstitutionOn",
    "OffsideGiven", "OffsideProvoked"
])]
df = df.drop(admin_events.index)

# drop lost aerial duels
lost_aerials = df.loc[
    (df["type_displayName"] == "Aerial") & (df["outcomeType_value"] == 0)
]
df = df.drop(lost_aerials.index)

# drop CornerAwarded
corners = df.loc[df["type_displayName"] == "CornerAwarded"]
df = df.drop(corners.index)

# drop goalkeeper-specific events
goalies = df.loc[df["type_displayName"].isin([
    "Save", "Claim", "Punch", "KeeperPickup",
    "KeeperSweeper", "PenaltyFaced"
])]
df = df.drop(goalies.index)
print(f"After filtering: {len(df)} events")

#%%
# Isolating possession chains

def isolateChains(df):
    df["nextTeamId"] = df.shift(-1, fill_value=0)["teamId"]
    chain_team = df.iloc[0]["teamId"]
    period = df.iloc[0]["period_value"]
    game = df.iloc[0]["game_id"]
    stop_criterion = 0
    chain = 0
    df["possesion_chain"] = 0
    df["possesion_chain_team"] = 0

    for i, row in df.iterrows():
        if row["period_value"] != period or row["game_id"] != game:
            chain += 1
            stop_criterion = 0
            chain_team = row["teamId"]
            period = row["period_value"]
            game = row["game_id"]

        df.at[i, "possesion_chain"] = chain
        df.at[i, "possesion_chain_team"] = chain_team

        if row["type_displayName"] in ("Pass", "Aerial"):
            if row["teamId"] == chain_team and row["outcomeType_value"] == 0:
                stop_criterion += 1
            if row["teamId"] != chain_team and row["outcomeType_value"] == 1:
                stop_criterion += 1

        if row["type_displayName"] in ("BallTouch", "BallRecovery"):
            if row["teamId"] == row["nextTeamId"]:
                stop_criterion += 2

        if row["type_displayName"] in ("MissedShots", "SavedShot", "Goal",
                                        "ShotOnPost", "Foul", "OffsidePass"):
            stop_criterion += 2

        if row["kickedOut"] == 1:
            stop_criterion += 2

        if stop_criterion >= 2:
            chain += 1
            stop_criterion = 0
            chain_team = row["nextTeamId"]

    return df

df = isolateChains(df)
print(f"Total chains: {df['possesion_chain'].nunique()}")

#%%
# Calculating xG for PL shots
"""Train the xG model on PL data and assign xG values to shots."""

def _is_penalty(qualifiers):
    if isinstance(qualifiers, list):
        for q in qualifiers:
            if q.get("type", {}).get("value") == 9:
                return True
    return False

shot_types = ("MissedShots", "SavedShot", "Goal", "ShotOnPost")

# fit xG model on PL non-penalty shots
all_shots = df.loc[
    (df["isShot"] == True) & (~df["qualifiers"].apply(_is_penalty))
].copy()
all_shots["X"] = (100 - all_shots["x"]) * 105 / 100
all_shots["C"] = abs(all_shots["y"] - 50) * 68 / 100
all_shots["Distance"] = np.sqrt(all_shots["X"]**2 + all_shots["C"]**2)
all_shots["Angle"] = np.where(
    np.arctan(7.32 * all_shots["X"] / (all_shots["X"]**2 + all_shots["C"]**2 - (7.32/2)**2)) > 0,
    np.arctan(7.32 * all_shots["X"] / (all_shots["X"]**2 + all_shots["C"]**2 - (7.32/2)**2)),
    np.arctan(7.32 * all_shots["X"] / (all_shots["X"]**2 + all_shots["C"]**2 - (7.32/2)**2)) + np.pi
)
all_shots["Goal"] = all_shots["isGoal"].apply(lambda x: 1 if x == True else 0)
all_shots["X2"] = all_shots["X"]**2
all_shots["C2"] = all_shots["C"]**2
all_shots["AX"] = all_shots["Angle"] * all_shots["X"]

xg_model_vars = ["Angle", "Distance", "X", "C", "X2", "C2", "AX"]
xg_formula = "Goal ~ " + " + ".join(xg_model_vars)
xg_model = smf.glm(formula=xg_formula, data=all_shots, family=sm.families.Binomial()).fit()
b = xg_model.params

def _compute_xg(sh):
    bsum = b.iloc[0]
    for i, v in enumerate(xg_model_vars):
        bsum = bsum + b.iloc[i + 1] * sh[v]
    return 1 / (1 + np.exp(-bsum))

# assign xG to df
df["xG"] = 0.0
all_shots["xG"] = all_shots.apply(_compute_xg, axis=1)
for index, row in all_shots.iterrows():
    df.at[index, "xG"] = row["xG"]

# penalties
pen_mask = (df["isShot"] == True) & (df["qualifiers"].apply(_is_penalty))
penalties = df.loc[pen_mask].copy()
if len(penalties) > 0:
    penalties["X"] = 11
    penalties["C"] = 0
    penalties["Distance"] = 11
    penalties["Angle"] = np.arctan(7.32 * 11 / (11**2 - (7.32/2)**2))
    penalties["X2"] = 121
    penalties["C2"] = 0
    penalties["AX"] = penalties["Angle"] * 11
    penalties["xG"] = penalties.apply(_compute_xg, axis=1)
    for index, row in penalties.iterrows():
        df.at[index, "xG"] = row["xG"]

print(f"Shots with xG: {(df['xG'] > 0).sum()}")

#%%
# Finding chains that ended with shot and preparing chains

def prepareChains(df):
    df["shot_end"] = 0
    no_chains = max(df["possesion_chain"].unique())
    indicies = []
    for i in range(no_chains + 1):
        possesion_chain_df = df.loc[df["possesion_chain"] == i]
        if len(possesion_chain_df) > 0:
            if possesion_chain_df.iloc[-1]["type_displayName"] in shot_types:
                df.loc[df["possesion_chain"] == i, "shot_end"] = 1
                xG = possesion_chain_df.iloc[-1]["xG"]
                df.loc[df["possesion_chain"] == i, "xG"] = xG
                k = i - 1
                if k > 0:
                    try:
                        prev = df.loc[df["possesion_chain"] == k]
                        while prev.iloc[-1]["type_displayName"] == "Foul":
                            df.loc[df["possesion_chain"] == k, "xG"] = xG
                            df.loc[df["possesion_chain"] == k, "shot_end"] = 1
                            k = k - 1
                            prev = df.loc[df["possesion_chain"] == k]
                    except:
                        k = k - 1
            team_indicies = possesion_chain_df.loc[
                possesion_chain_df["teamId"] == possesion_chain_df.teamId.mode().iloc[0]
            ].index.values.tolist()
            indicies.extend(team_indicies)
    df = df.loc[indicies]
    return df

df = prepareChains(df)
print(f"Chains ending with shot: {df.loc[df['shot_end'] == 1, 'possesion_chain'].nunique()}")

#%%
# Preparing coordinates and filtering events with end coordinates

df = df.loc[df["endX"].notna() | df["type_displayName"].isin(shot_types)]
df["x0"] = df["x"] * 105 / 100
df["c0"] = abs(50 - df["y"]) * 68 / 100
df["x1"] = df["endX"] * 105 / 100
df["c1"] = abs(50 - df["endY"]) * 68 / 100
df.loc[df["type_displayName"].isin(shot_types), "x1"] = 105
df.loc[df["type_displayName"].isin(shot_types), "c1"] = 0

print(f"Events with coordinates: {len(df)}")

#%%
# Preparing polynomial variables for models

var = ["x0", "x1", "c0", "c1"]

inputs = []
inputs.extend(combinations_with_replacement(var, 1))
inputs.extend(combinations_with_replacement(var, 2))
inputs.extend(combinations_with_replacement(var, 3))

for i in inputs:
    if len(i) > 1:
        column = ""
        x = 1
        for c in i:
            column += c
            x = x * df[c]
        df[column] = x
        var.append(column)

print(f"Polynomial variables: {len(var)}")

#%%
# Extracting qualifier-based binary features for passes (xA-specific)
"""These features differentiate xA from xT by capturing pass type information
relevant to assist quality."""

def extract_pass_qualifiers(qualifiers):
    """Extract binary features from Opta pass qualifiers."""
    qual_values = set()
    if isinstance(qualifiers, (list, np.ndarray)):
        for q in qualifiers:
            qual_values.add(q["type"]["value"])
    return {
        "is_cross": int(2 in qual_values),
        "is_through_ball": int(4 in qual_values),
        "is_freekick": int(5 in qual_values),
        "is_corner": int(6 in qual_values),
        "is_offensive": int(286 in qual_values),
    }

passes = df.loc[df["type_displayName"] == "Pass"].copy()
qual_features = passes["qualifiers"].apply(extract_pass_qualifiers)
qual_df = pd.DataFrame(qual_features.tolist(), index=passes.index)
passes = pd.concat([passes, qual_df], axis=1)

xA_extra_features = ["is_cross", "is_through_ball", "is_freekick", "is_corner", "is_offensive"]
xA_var = var + xA_extra_features

print(f"xA model variables: {len(xA_var)} ({len(var)} polynomial + {len(xA_extra_features)} qualifier)")
print(f"Qualifier feature counts:")
for feat in xA_extra_features:
    print(f"  {feat}: {passes[feat].sum()}")

#%%
# Identifying assist passes and building training labels
"""Find passes that assisted a shot by looking up relatedEventId on shots.
eventId is local per game, so we filter by game_id to avoid cross-game collisions."""

# find all shots with a relatedEventId
shots_with_rel = df.loc[
    (df["isShot"] == True) & (df["relatedEventId"].notna())
].copy()

# build mapping: (game_id, eventId) -> xG for assist passes
assist_event_keys = set()
assist_xg_map = {}

for _, shot in shots_with_rel.iterrows():
    rel_id = int(shot["relatedEventId"])
    gid = shot["game_id"]
    # look up the related event in same game
    related = df.loc[(df["eventId"] == rel_id) & (df["game_id"] == gid)]
    if len(related) > 0 and related.iloc[0]["type_displayName"] == "Pass":
        key = (gid, rel_id)
        assist_event_keys.add(key)
        assist_xg_map[key] = shot["xG"]

# label passes
passes["_key"] = list(zip(passes["game_id"], passes["eventId"]))
passes["is_assist"] = passes["_key"].isin(assist_event_keys).astype(int)
passes["assist_xG"] = passes["_key"].map(assist_xg_map).fillna(0.0)
passes = passes.drop(columns=["_key"])

n_assists = passes["is_assist"].sum()
n_passes = len(passes)
print(f"Assist passes: {n_assists} / {n_passes} total passes ({100*n_assists/n_passes:.2f}%)")

#%%
# Training xA two-step model
"""Step 1: GradientBoostingClassifier for P(this pass assists a shot)
Step 2: LinearRegression for E[xG | assist occurred]"""

X = passes[xA_var].values
y_step1 = passes["is_assist"].values

# Step 1: assist probability model
xA_gbc = GradientBoostingClassifier(
    n_estimators=100, max_depth=4, min_samples_leaf=10, random_state=123
)
xA_gbc.fit(X, y_step1)
print(f"xA GBC training score: {xA_gbc.score(X, y_step1):.4f}")

# Step 2: xG prediction model (trained on assist passes only)
assist_passes = passes.loc[passes["is_assist"] == 1]
X_step2 = assist_passes[xA_var].values
y_step2 = assist_passes["assist_xG"].values

xA_lr = LinearRegression()
xA_lr.fit(X_step2, y_step2)
print(f"xA LR training R²: {xA_lr.score(X_step2, y_step2):.4f}")

#%%
# Saving trained models and variable list
"""Save both models and the variable list so xA_brasileirao.py can load them."""

dump(xA_gbc, "xA_gbc_model.joblib")
dump(xA_lr, "xA_lr_model.joblib")
dump(xA_var, "xA_model_vars.joblib")
print("Models saved: xA_gbc_model.joblib, xA_lr_model.joblib, xA_model_vars.joblib")
