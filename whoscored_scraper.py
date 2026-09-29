#%%
# MatchAnalysis 2025 — Orchestrator
import pandas as pd
import numpy as np
import json
# plotting
import os
#import pathlib
import warnings
#import statsmodels.api as sm
#import statsmodels.formula.api as smf
#from mplsoccer import Pitch
#import matplotlib.pyplot as plt
import soccerdata as sd
from multimethod import multimethod
from multimethod import overload
from socceraction.data.opta import OptaLoader
import socceraction.spadl as spadl
#import socceraction.xthreat as xthreat
#from shapely.geometry import Point, Polygon
#from scipy.spatial import ConvexHull
#from scipy.stats import zscore
#from scipy.stats import rankdata
#from tqdm import tqdm
#from scipy.stats import poisson

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')


ws = sd.WhoScored(leagues="BRA-Brasileirão", seasons=2025)

# Scrape all games and return a OptaLoader object
loader = ws.read_events(output_fmt='loader')

# Game events
events = ws.read_events()

# Game schedule
df_schedule = ws.read_schedule()

